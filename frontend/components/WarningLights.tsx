"use client";
import { t } from "@/lib/i18n";

/** Voyants courants du tableau de bord, dessinés pour DALIL (simplifiés, d'après les symboles usuels).
 * Toucher un voyant ajoute sa description au texte : la chaîne de diagnostic habituelle s'en charge (vérifié le
 * 28/11/2026 : chaque phrase mène à la bonne panne type). L'ABS et l'airbag n'y sont pas : aucune panne type ne leur
 * correspond encore. Les voyants « stop » affichent tout de suite le conseil de sûreté. */
export type Light = { id: string; color: "red" | "orange"; stop: boolean; icon: React.ReactNode };

const S = { fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

export const LIGHTS: Light[] = [
  { id: "moteur", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><path d="M5 9h3V7h4V5h7v2h3l2 3h2v-2h2v8h-2v-2h-2l-3 3h-9l-2-2H8v2H5z" /><path d="M2 10v5M2 12.5h3" /></svg>) },
  { id: "huile", color: "red", stop: true, icon: (
    <svg viewBox="0 0 32 24" {...S}><path d="M4 11h3l3-2h8l8-3-6 8H9l-2-3" /><path d="M10 9V7h3M14 14v3h-4" /><path d="M28 13c0 1.2-.8 2-1.5 2S25 14.2 25 13s1.5-3 1.5-3S28 11.8 28 13z" /></svg>) },
  { id: "batterie", color: "red", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><rect x="4" y="7" width="24" height="13" rx="1.5" /><path d="M8 7V5h4v2M20 7V5h4v2M9 13.5h4M11 11.5v4M19 13.5h4" /></svg>) },
  { id: "temperature", color: "red", stop: true, icon: (
    <svg viewBox="0 0 32 24" {...S}><path d="M14 4h4v9a3.5 3.5 0 1 1-4 0z" /><path d="M18 7h3M18 10h3" /><path d="M4 20c2-1.5 4 1.5 6 0s4 1.5 6 0 4 1.5 6 0 4 1.5 6 0" /></svg>) },
  { id: "frein", color: "red", stop: true, icon: (
    <svg viewBox="0 0 32 24" {...S}><circle cx="16" cy="12" r="7" /><path d="M7 5a10 10 0 0 0 0 14M25 5a10 10 0 0 1 0 14M16 8.5v4.5" /><circle cx="16" cy="15.6" r=".4" fill="currentColor" /></svg>) },
  { id: "plaquettes", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><circle cx="16" cy="12" r="6" /><path d="M7 5a10 10 0 0 0 0 14M25 5a10 10 0 0 1 0 14" strokeDasharray="2.5 2" /></svg>) },
  { id: "prechauffage", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><path d="M4 12c2-6 5-6 6 0s4 6 6 0 4-6 6 0 4 6 6 0" /></svg>) },
  { id: "fap", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><rect x="6" y="5" width="20" height="14" rx="3" /><path d="M2 12h4M26 12h4" />
      {[10, 14, 18, 22].flatMap((x) => [9, 15].map((y) => <circle key={`${x}${y}`} cx={x} cy={y} r=".9" fill="currentColor" />))}</svg>) },
  { id: "direction", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><circle cx="14" cy="12" r="8" /><circle cx="14" cy="12" r="2" /><path d="M6.5 10.5h5.5M16.5 10.5h5M14 14v6M27 6v7" /><circle cx="27" cy="17" r=".5" fill="currentColor" /></svg>) },
  { id: "vidange", color: "orange", stop: false, icon: (
    <svg viewBox="0 0 32 24" {...S}><path d="M9 19l8.5-8.5a4.5 4.5 0 1 0-3-3L6 16z" /><path d="M20 5.5l-2 2 2 2 2-2" /></svg>) },
];

export default function WarningLights({ selected, onToggle }: { selected: string[]; onToggle: (l: Light) => void }) {
  const stop = LIGHTS.filter((l) => l.stop && selected.includes(l.id));
  return (
    <div>
      <div className="lights" role="group" aria-label={t("lights.title")}>
        {LIGHTS.map((l) => (
          <button key={l.id} type="button" className={`light light-${l.color}`} aria-pressed={selected.includes(l.id)}
            onClick={() => onToggle(l)}>
            <span className="light-icon" aria-hidden>{l.icon}</span>
            <span className="light-name">{t(`lights.${l.id}`)}</span>
          </button>
        ))}
      </div>
      {stop.length > 0 && (
        <div className="danger" role="alert">{stop.map((l) => t(`lights.${l.id}.stop`)).join(" ")}</div>
      )}
    </div>
  );
}

/** Phrase ajoutée au texte de la panne pour un voyant. */
export const lightPhrase = (id: string) => t(`lights.${id}.phrase`);
