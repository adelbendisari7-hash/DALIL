/** Rendez-vous d'agenda (.ics) préparé sur le téléphone, sans serveur : l'agenda du téléphone prévient lui-même,
 * même DALIL fermé (les notifications de DALIL demandent le https, voir l'étape 12). Rien n'est envoyé ailleurs. */
export type Reminder = { title: string; description: string; day: string /* AAAA-MM-JJ */; alarmsDaysBefore: number[]; uid: string };

const esc = (s: string) => s.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
const compact = (d: string) => d.replaceAll("-", "");

export function icsText(r: Reminder): string {
  const next = new Date(`${r.day}T12:00:00Z`);
  next.setUTCDate(next.getUTCDate() + 1);
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
  // Rappel à 9 h le jour voulu : l'événement dure toute la journée et commence à minuit, d'où n x 24 h - 9 h
  const trigger = (n: number) => { const h = n * 24 - 9; return h > 0 ? `-PT${h}H` : `PT${-h}H`; };
  const alarms = r.alarmsDaysBefore.flatMap((n) => [
    "BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${esc(r.title)}`, `TRIGGER:${trigger(n)}`, "END:VALARM",
  ]);
  return [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DALIL//Rappels//FR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    "BEGIN:VEVENT", `UID:${r.uid}@dalil`, `DTSTAMP:${stamp}`,
    `DTSTART;VALUE=DATE:${compact(r.day)}`, `DTEND;VALUE=DATE:${next.toISOString().slice(0, 10).replaceAll("-", "")}`,
    `SUMMARY:${esc(r.title)}`, `DESCRIPTION:${esc(r.description)}`, "TRANSP:TRANSPARENT",
    ...alarms, "END:VEVENT", "END:VCALENDAR", "",
  ].join("\r\n");
}

/** Ouvre le fichier : sur un téléphone, l'agenda propose d'ajouter le rendez-vous. */
export function downloadIcs(r: Reminder, filename: string) {
  const blob = new Blob([icsText(r)], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
