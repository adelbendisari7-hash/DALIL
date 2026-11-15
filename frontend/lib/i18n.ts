import fr from "@/messages/fr.json";
import ar from "@/messages/ar.json";

const catalogs: Record<string, Record<string, string>> = { fr, ar };
export type Lang = "fr" | "ar";
let current: Lang = "fr";

export function setLang(l: Lang) {
  current = l;
}

/** Tout texte d'interface passe par ici. Les {variables} sont remplacées ; repli sur le français. */
export function t(key: string, vars?: Record<string, string | number>): string {
  let s = catalogs[current]?.[key] ?? (fr as Record<string, string>)[key] ?? key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, String(v));
  return s;
}
