// Par défaut, même adresse que le site (relais vers l'API dans next.config) ; NEXT_PUBLIC_API_URL pour une API ailleurs.
export const API = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export type User = {
  id: number; phone: string; role: string; name: string | null; consent: boolean;
  // Compte client : prénom, nom obligatoires (`complete`) ; le reste facultatif
  first_name?: string | null; last_name?: string | null; email?: string | null; commune_id?: number | null;
  birth_date?: string | null; lang?: string; complete?: boolean;
};

/** Voiture du compte client (GET /me/vehicles). */
export type UserCar = {
  id: number; plate: string; variant_id: number | null; year: number | null; label: string | null; nickname: string | null;
  mileage_km: number | null; vin: string | null; display: string;
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
  constructor(public status: number, message: string, public code?: string) {
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
      throw new ApiError(res.status, o.message ?? "", o.code);
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
