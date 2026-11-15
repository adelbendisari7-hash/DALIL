export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export type User = { id: number; phone: string; role: string; name: string | null; consent: boolean };

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
  constructor(public status: number, message: string) {
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
    const msg = typeof d === "string" ? d : Array.isArray(d) ? d.map((x: { msg?: string }) => x.msg).join(" ; ") : "";
    throw new ApiError(res.status, msg);
  }
  return data as T;
}

export type Vehicle = { variantId: number; label: string; brand: string; model: string };

export const vehicleStore = {
  get: (): Vehicle | null => {
    const v = read("dalil.vehicle");
    return v ? (JSON.parse(v) as Vehicle) : null;
  },
  set: (v: Vehicle | null) => write("dalil.vehicle", v ? JSON.stringify(v) : null),
};
