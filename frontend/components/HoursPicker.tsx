"use client";
import { t } from "@/lib/i18n";

/** Horaires structurés (pour « ouvert maintenant ») : jours en pastilles, heure d'ouverture et de fermeture,
 * pause facultative. Jours de la semaine de Python côté serveur : lundi = 0 ... dimanche = 6. */
export type Opening = { days: number[]; from: string; to: string; break?: [string, string] | null };

// Semaine algérienne : samedi d'abord
const WEEK = [5, 6, 0, 1, 2, 3, 4];
export const DEFAULT_OPENING: Opening = { days: [5, 6, 0, 1, 2, 3], from: "08:00", to: "18:00", break: null };

export default function HoursPicker({ value, onChange }: { value: Opening; onChange: (o: Opening) => void }) {
  const toggle = (d: number) =>
    onChange({ ...value, days: value.days.includes(d) ? value.days.filter((x) => x !== d) : [...value.days, d] });
  return (
    <fieldset className="hours" style={{ border: 0, padding: 0, margin: 0 }}>
      <legend className="sr-label">{t("shop.hours")}</legend>
      <span className="help">{t("shop.hours.days")}</span>
      <div className="chips">
        {WEEK.map((d) => (
          <button key={d} type="button" className="chip" aria-pressed={value.days.includes(d)} onClick={() => toggle(d)}>
            {t(`day.${d}`)}
          </button>
        ))}
      </div>
      <div className="row">
        <div>
          <label htmlFor="h-from">{t("shop.hours.from")}</label>
          <input id="h-from" type="time" value={value.from} onChange={(e) => onChange({ ...value, from: e.target.value })} />
        </div>
        <div>
          <label htmlFor="h-to">{t("shop.hours.to")}</label>
          <input id="h-to" type="time" value={value.to} onChange={(e) => onChange({ ...value, to: e.target.value })} />
        </div>
      </div>
      <label className="check">
        <input type="checkbox" checked={Boolean(value.break)}
          onChange={(e) => onChange({ ...value, break: e.target.checked ? ["12:00", "13:30"] : null })} />
        <span>{t("shop.hours.break")}</span>
      </label>
      {value.break && (
        <div className="row">
          <div>
            <label htmlFor="h-b1">{t("shop.hours.breakFrom")}</label>
            <input id="h-b1" type="time" value={value.break[0]} onChange={(e) => onChange({ ...value, break: [e.target.value, value.break![1]] })} />
          </div>
          <div>
            <label htmlFor="h-b2">{t("shop.hours.breakTo")}</label>
            <input id="h-b2" type="time" value={value.break[1]} onChange={(e) => onChange({ ...value, break: [value.break![0], e.target.value] })} />
          </div>
        </div>
      )}
    </fieldset>
  );
}

/** Pour l'API : sans pause, le champ est retiré. */
export function cleanOpening(o: Opening | null): Record<string, unknown> | null {
  if (!o) return null;
  const { break: b, ...rest } = o;
  return b ? { ...rest, break: b } : rest;
}
