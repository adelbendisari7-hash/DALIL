// Par défaut, même adresse que le site (relais vers l'API dans next.config) ; NEXT_PUBLIC_API_URL pour une API ailleurs.
export const API = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export type User = {
  id: number; phone: string; role: string; name: string | null; consent: boolean;
  // Compte client : prénom, nom obligatoires (`complete`) ; le reste facultatif
  first_name?: string | null; last_name?: string | null; email?: string | null; commune_id?: number | null;
  birth_date?: string | null; lang?: string; complete?: boolean; has_password?: boolean;
};

/** Voiture du compte client (GET /me/vehicles). */
export type UserCar = {
  id: number; plate: string; variant_id: number | null; year: number | null; label: string | null; nickname: string | null;
  mileage_km: number | null; vin: string | null; display: string; maintenance_due?: number;
  // Entretiens dépassés (« due ») ou proches (« soon ») : rappel sur l'accueil
  maintenance_items?: { item: string; name: string; status: "due" | "soon"; km_left: number | null; days_left: number | null }[];
};

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function write(key: string, value: string | null) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    /* stockage indisponible (navigation privée) : l'application fonctionne sans */
  }
}

export const session = {
  token: () => read("dalil.token"),
  user: (): User | null => {
    const u = read("dalil.user");
    return u ? (JSON.parse(u) as User) : null;
  },
  save: (token: string, user: User) => {
    write("dalil.token", token);
    write("dalil.user", JSON.stringify(user));
    window.dispatchEvent(new Event("dalil-auth"));
  },
  clear: () => {
    write("dalil.token", null);
    write("dalil.user", null);
    window.dispatchEvent(new Event("dalil-auth"));
  },
};

export const store = { read, write };

export class ApiError extends Error {
  /** `code` : erreur métier nommée par l'API (exemple : « plate_taken », matricule déjà enregistré). */
  constructor(public status: number, message: string, public code?: string, public data?: Record<string, unknown>) {
    super(message);
  }
}

export async function api<T = unknown>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = session.token();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, { ...init, headers, body });
  } catch {
    throw new ApiError(0, "");
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = (data as { detail?: unknown }).detail;
    // Erreurs de validation (FastAPI/pydantic) : on garde le message en français, sans le préfixe technique « Value error, ».
    if (d && typeof d === "object" && !Array.isArray(d)) {
      const o = d as { code?: string; message?: string };
      throw new ApiError(res.status, o.message ?? "", o.code, d as Record<string, unknown>);
    }
    const msg = typeof d === "string" ? d : Array.isArray(d)
      ? d.map((x: { msg?: string }) => (x.msg ?? "").replace(/^Value error,\s*/i, "")).join(" ; ") : "";
    throw new ApiError(res.status, msg);
  }
  return data as T;
}

export type Vehicle = { variantId: number; label: string; brand: string; model: string; year?: number | null };

export const vehicleStore = {
  get: (): Vehicle | null => {
    const v = read("dalil.vehicle");
    return v ? (JSON.parse(v) as Vehicle) : null;
  },
  set: (v: Vehicle | null) => write("dalil.vehicle", v ? JSON.stringify(v) : null),
};

/** Demandes envoyées aux magasins depuis cet appareil (suivi sans compte : identifiant + jeton secret). */
export type RequestRef = { id: number; token: string };
export const requestStore = {
  list: (): RequestRef[] => {
    try { return JSON.parse(read("dalil.requests") || "[]") as RequestRef[]; } catch { return []; }
  },
  add: (r: RequestRef) => {
    const all = [r, ...requestStore.list().filter((x) => x.id !== r.id)].slice(0, 30);
    write("dalil.requests", JSON.stringify(all));
  },
};

/** Dernier diagnostic et ses magasins, gardés sur l'appareil pour les relire sans réseau (au garage, quand la 3G
 * coupe). Marche aussi en http (le service worker, lui, demande le https ou localhost). Rien n'est envoyé ailleurs. */
export type LastDiagnosis = {
  id: number; savedAt: string; result: unknown;
  shops?: { categoryId: number; partName: string; savedAt: string; list: unknown[] };
};
export const lastDiagnosis = {
  get: (): LastDiagnosis | null => {
    try { return JSON.parse(read("dalil.last") || "null") as LastDiagnosis | null; } catch { return null; }
  },
  saveResult: (id: number, result: unknown) => {
    const cur = lastDiagnosis.get();
    const keep = cur && cur.id === id ? cur.shops : undefined;   // les magasins du même diagnostic restent
    write("dalil.last", JSON.stringify({ id, savedAt: new Date().toISOString(), result, shops: keep }));
  },
  saveShops: (sessionId: number, categoryId: number, partName: string, list: unknown[]) => {
    const cur = lastDiagnosis.get();
    if (!cur || cur.id !== sessionId) return;
    write("dalil.last", JSON.stringify({ ...cur, shops: { categoryId, partName, savedAt: new Date().toISOString(), list } }));
  },
  clear: () => write("dalil.last", null),
};
