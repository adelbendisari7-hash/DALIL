"use client";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type Paper, type UserCar } from "@/lib/api";
import { downloadIcs } from "@/lib/ics";
import { t } from "@/lib/i18n";

type Kind = "controle" | "assurance";
const KINDS: Kind[] = ["controle", "assurance"];
type Data = { current: Record<Kind, Paper | null>; history: Paper[] };
type Draft = { done_on: string; valid_until: string; provider: string; price: string; note: string };

const day = (iso: string) => new Date(iso).toLocaleDateString("fr-FR");
const da = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} DA`;
const today = () => new Date().toISOString().slice(0, 10);

function addMonths(iso: string, months: number): string {
  const d = new Date(`${iso}T12:00:00Z`);
  const target = d.getUTCDate();
  d.setUTCDate(1);
  d.setUTCMonth(d.getUTCMonth() + months);
  const last = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)).getUTCDate();
  d.setUTCDate(Math.min(target, last));
  d.setUTCDate(d.getUTCDate() - 1);   // valable jusqu'à la veille de la même date
  return d.toISOString().slice(0, 10);
}

/** « Expiré depuis 3 jours », « dernier jour », « dans 12 jours » */
export function paperWhen(p: Paper): string {
  if (p.days_left < 0) return t(p.days_left === -1 ? "papers.expired1" : "papers.expiredN", { n: -p.days_left });
  if (p.days_left === 0) return t("papers.lastDay");
  return t(p.days_left === 1 ? "papers.in1" : "papers.inN", { n: p.days_left });
}

function PaperForm({ kind, draft, onSave, onCancel }: {
  kind: Kind; draft: Draft; onSave: (d: Draft) => Promise<string | null>; onCancel: () => void;
}) {
  const [d, setD] = useState(draft);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof Draft, v: string) => setD({ ...d, [k]: v });
  const id = (k: string) => `p-${kind}-${k}`;

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!d.valid_until) return setMsg(t("papers.needEnd"));
    setBusy(true);
    const err = await onSave(d);
    setBusy(false);
    if (err !== null) setMsg(err);
  }

  return (
    <form className="car-form visit-form" onSubmit={save} noValidate>
      <label htmlFor={id("done")}>{t(`papers.${kind}.done`)}</label>
      <input id={id("done")} type="date" value={d.done_on} max={today()} onChange={(e) => set("done_on", e.target.value)} />
      <label htmlFor={id("end")}>{t("papers.validUntil")}</label>
      <input id={id("end")} type="date" value={d.valid_until} onChange={(e) => set("valid_until", e.target.value)} />
      {/* Raccourcis à partir de la date où il a été fait ; la date du document fait foi */}
      <div className="chips">
        {[6, 12, 24].map((m) => (
          <button key={m} type="button" className="chip" onClick={() => set("valid_until", addMonths(d.done_on || today(), m))}>
            {t(`papers.plus${m}`)}
          </button>
        ))}
      </div>
      <p className="help">{t(`papers.${kind}.help`)}</p>
      <label htmlFor={id("provider")}>{t(`papers.${kind}.provider`)}</label>
      <input id={id("provider")} maxLength={120} value={d.provider} onChange={(e) => set("provider", e.target.value)} />
      <label htmlFor={id("price")}>{t("carnet.price")}</label>
      <input id={id("price")} inputMode="numeric" value={d.price} placeholder={t("carnet.price.placeholder")}
        onChange={(e) => set("price", e.target.value.replace(/\D/g, ""))} />
      <label htmlFor={id("note")}>{t("carnet.note")}</label>
      <input id={id("note")} maxLength={300} value={d.note} placeholder={t(`papers.${kind}.note`)} onChange={(e) => set("note", e.target.value)} />
      {msg && <p className="err" role="alert">{msg}</p>}
      <div className="actions">
        <button className="btn" disabled={busy}>{t("papers.save")}</button>
        <button type="button" className="btn btn-ghost" onClick={onCancel}>{t("account.cars.cancel")}</button>
      </div>
    </form>
  );
}

/** Contrôle technique et assurance d'une voiture : fait le, valable jusqu'au, rappel dès 30 jours avant la fin,
 * rendez-vous à ajouter à l'agenda du téléphone, historique des renouvellements. */
export default function Papers({ car, onChange }: { car: UserCar; onChange: () => void }) {
  const [data, setData] = useState<Data | null>(null);
  const [open, setOpen] = useState<{ kind: Kind; doc: Paper | null } | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const load = useCallback(() => {
    api<Data>(`/me/vehicles/${car.id}/papers`).then(setData).catch(() => setData(null));
  }, [car.id]);
  useEffect(() => { load(); }, [load]);

  function saver(kind: Kind, doc: Paper | null) {
    return async (d: Draft): Promise<string | null> => {
      try {
        await api(doc ? `/me/vehicles/${car.id}/papers/${doc.id}` : `/me/vehicles/${car.id}/papers`, {
          method: doc ? "PUT" : "POST",
          json: { kind, done_on: d.done_on || null, valid_until: d.valid_until, provider: d.provider.trim() || null,
                  price: d.price ? Number(d.price) : null, note: d.note.trim() || null },
        });
        setOpen(null);
        load();
        onChange();
        window.dispatchEvent(new Event("dalil-alerts"));
        return null;
      } catch (e) {
        return e instanceof ApiError && e.message ? e.message : t("common.error");
      }
    };
  }

  async function remove(p: Paper) {
    if (!window.confirm(t("papers.remove.confirm"))) return;
    await api(`/me/vehicles/${car.id}/papers/${p.id}`, { method: "DELETE" }).catch(() => undefined);
    load();
    onChange();
    window.dispatchEvent(new Event("dalil-alerts"));
  }

  function agenda(kind: Kind, p: Paper) {
    const name = car.nickname || car.display;
    downloadIcs({
      uid: `papier-${p.id}`, day: p.valid_until, alarmsDaysBefore: [7, 1],
      title: t(`papers.${kind}.agendaTitle`, { car: name }),
      description: t("papers.agendaText", { car: name, plate: car.plate, date: day(p.valid_until) }),
    }, `dalil-${kind}-${car.plate.replace(/\W/g, "")}.ics`);
  }

  if (!data) return <p>{t("common.loading")}</p>;
  const blank = (kind: Kind, from: Paper | null): Draft => from
    ? { done_on: from.done_on ?? "", valid_until: from.valid_until, provider: from.provider ?? "", price: from.price != null ? String(from.price) : "", note: from.note ?? "" }
    : { done_on: today(), valid_until: "", provider: data.current[kind]?.provider ?? "", price: "", note: "" };

  return (
    <div className="maintenance papers">
      <ul className="list">
        {KINDS.map((kind) => {
          const p = data.current[kind];
          const editing = open?.kind === kind;
          return (
            <li key={kind} className={`maint paper is-${p?.status ?? "none"}`}>
              <div style={{ width: "100%" }}>
                <div className="status-head">
                  <strong>{t(`papers.${kind}`)}</strong>
                  <span className={`maint-pill paper-pill is-${p?.status ?? "none"}`}>{t(`papers.status.${p?.status ?? "none"}`)}</span>
                </div>
                {p ? (
                  <>
                    <span className="meta">
                      {t("papers.until", { date: day(p.valid_until) })}
                      {p.status !== "ok" && <> · <strong className={p.status === "soon" ? undefined : "paper-urgent"}>{paperWhen(p)}</strong></>}
                    </span>
                    {(p.provider || p.done_on) && (
                      <><br /><span className="meta">{[p.done_on && t("papers.doneOn", { date: day(p.done_on) }), p.provider, p.price != null && da(p.price)].filter(Boolean).join(" · ")}</span></>
                    )}
                  </>
                ) : (
                  <span className="meta">{t(`papers.${kind}.empty`)}</span>
                )}
                {editing ? (
                  <PaperForm kind={kind} draft={blank(kind, open!.doc)} onSave={saver(kind, open!.doc)} onCancel={() => setOpen(null)} />
                ) : (
                  <div className="actions" style={{ marginTop: "0.4rem" }}>
                    <button type="button" className="btn btn-ghost" onClick={() => setOpen({ kind, doc: null })}
                      aria-label={t(p ? "papers.renewFor" : "papers.addFor", { name: t(`papers.${kind}`) })}>
                      {t(p ? "papers.renew" : "papers.add")}
                    </button>
                    {p && p.days_left >= 0 && (
                      <button type="button" className="btn btn-ghost" onClick={() => agenda(kind, p)}>{t("papers.agenda")}</button>
                    )}
                    {p && <button type="button" className="chip" onClick={() => setOpen({ kind, doc: p })}>{t("carnet.edit")}</button>}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ul>
      <p className="help">{t("papers.reminders")}</p>
      {data.history.length > KINDS.filter((k) => data.current[k]).length && (
        <>
          <button type="button" className="btn btn-ghost" aria-expanded={showHistory} onClick={() => setShowHistory(!showHistory)}>
            {t("papers.history")}
          </button>
          {showHistory && (
            <ol className="carnet-list">
              {data.history.map((p) => (
                <li key={p.id} className="visit">
                  <div className="status-head">
                    <strong>{t(`papers.${p.kind}`)}</strong>
                    <span className="meta">{p.done_on ? `${day(p.done_on)} → ` : ""}{day(p.valid_until)}</span>
                  </div>
                  {(p.provider || p.price != null || p.note) && (
                    <span className="meta">{[p.provider, p.price != null && da(p.price), p.note].filter(Boolean).join(" · ")}</span>
                  )}
                  <div className="actions" style={{ marginTop: "0.3rem" }}>
                    <button type="button" className="chip" onClick={() => remove(p)}
                      aria-label={t("papers.removeFor", { name: t(`papers.${p.kind}`), date: day(p.valid_until) })}>{t("carnet.remove")}</button>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </>
      )}
    </div>
  );
}
