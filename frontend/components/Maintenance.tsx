"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type UserCar } from "@/lib/api";
import { t } from "@/lib/i18n";

type Item = {
  item: string; name: string; why: string; every_km: number; every_months: number;
  status: "due" | "soon" | "check" | "ok" | "unknown"; next_km: number | null; next_date: string | null;
  km_left: number | null; days_left: number | null; last: { id: number; km: number | null; done_on: string } | null;
  part: { category_id: number; name: string } | null;
};
type Visit = {
  id: number; done_on: string; km: number | null; price: number | null; place: string | null; note: string | null;
  operations: { id: number; item: string; name: string }[];
};
type History = { visits: Visit[]; total: number; total_12_months: number; priced: number };

const km = (n: number) => `${n.toLocaleString("fr-FR")} km`;
const da = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} DA`;
const day = (iso: string) => new Date(iso).toLocaleDateString("fr-FR");
const today = () => new Date().toISOString().slice(0, 10);

type Draft = { items: string[]; other: string; km: string; date: string; price: string; place: string; note: string };

/** Formulaire d'un passage au garage : opérations en pastilles (plusieurs à la fois), autre chose en texte libre,
 * date, kilométrage à ce moment-là, prix payé, garage ou magasin, remarque. Sert à noter et à corriger. */
function VisitForm({ all, draft, onSave, onCancel, saveLabel }: {
  all: Item[]; draft: Draft; saveLabel: string;
  onSave: (d: Draft) => Promise<string | null>; onCancel: () => void;
}) {
  const [d, setD] = useState<Draft>(draft);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof Draft, v: string) => setD({ ...d, [k]: v });
  const toggle = (slug: string) => setD({ ...d, items: d.items.includes(slug) ? d.items.filter((x) => x !== slug) : [...d.items, slug] });

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!d.items.length && !d.other.trim()) return setMsg(t("carnet.pickOne"));
    setBusy(true);
    const err = await onSave(d);
    setBusy(false);
    if (err !== null) setMsg(err);
  }

  return (
    <form className="car-form visit-form" onSubmit={save} noValidate>
      <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
        <legend className="label-like">{t("carnet.ops")}</legend>
        <div className="chips">
          {all.map((it) => (
            <button key={it.item} type="button" className="chip" aria-pressed={d.items.includes(it.item)} onClick={() => toggle(it.item)}>
              {it.name}
            </button>
          ))}
        </div>
      </fieldset>
      <label htmlFor="v-other">{t("carnet.other")}</label>
      <input id="v-other" maxLength={80} value={d.other} placeholder={t("carnet.other.placeholder")} onChange={(e) => set("other", e.target.value)} />
      <label htmlFor="v-date">{t("maint.date")}</label>
      <input id="v-date" type="date" value={d.date} max={today()} onChange={(e) => set("date", e.target.value)} style={{ maxWidth: "14rem" }} />
      <div className="row">
        <div>
          <label htmlFor="v-km">{t("carnet.km")}</label>
          <input id="v-km" inputMode="numeric" value={d.km} onChange={(e) => set("km", e.target.value.replace(/\D/g, ""))} />
        </div>
        <div>
          <label htmlFor="v-price">{t("carnet.price")}</label>
          <input id="v-price" inputMode="numeric" value={d.price} placeholder={t("carnet.price.placeholder")}
            onChange={(e) => set("price", e.target.value.replace(/\D/g, ""))} />
        </div>
      </div>
      <label htmlFor="v-place">{t("carnet.place")}</label>
      <input id="v-place" maxLength={120} value={d.place} placeholder={t("carnet.place.placeholder")} onChange={(e) => set("place", e.target.value)} />
      <label htmlFor="v-note">{t("carnet.note")}</label>
      <input id="v-note" maxLength={300} value={d.note} placeholder={t("carnet.note.placeholder")} onChange={(e) => set("note", e.target.value)} />
      {msg && <p className="err" role="alert">{msg}</p>}
      <div className="actions">
        <button className="btn" disabled={busy}>{saveLabel}</button>
        <button type="button" className="btn btn-ghost" onClick={onCancel}>{t("account.cars.cancel")}</button>
      </div>
    </form>
  );
}

/** Entretien d'une voiture : prochaines échéances (à faire, bientôt, à vérifier) et carnet d'entretien (passages au
 * garage avec date, kilométrage, prix, garage). Intervalles indicatifs : le carnet du constructeur fait foi. */
export default function Maintenance({ car, onChange }: { car: UserCar; onChange: () => void }) {
  const [items, setItems] = useState<Item[] | null>(null);
  const [history, setHistory] = useState<History | null>(null);
  // Formulaire ouvert : « new » (passage libre), le slug d'une échéance (« Fait »), ou l'identifiant d'un passage à corriger
  const [open, setOpen] = useState<string | number | null>(null);

  const load = useCallback(() => {
    api<{ items: Item[] }>(`/me/vehicles/${car.id}/maintenance`).then((r) => setItems(r.items)).catch(() => setItems([]));
    api<History>(`/me/vehicles/${car.id}/maintenance/history`).then(setHistory).catch(() => setHistory(null));
  }, [car.id]);
  useEffect(() => { load(); }, [load]);

  const blank = (slugs: string[]): Draft => ({ items: slugs, other: "", km: car.mileage_km != null ? String(car.mileage_km) : "",
    date: today(), price: "", place: "", note: "" });
  const fromVisit = (v: Visit): Draft => ({
    items: v.operations.filter((o) => o.item !== "autre").map((o) => o.item),
    other: v.operations.find((o) => o.item === "autre")?.name ?? "",
    km: v.km != null ? String(v.km) : "", date: v.done_on, price: v.price != null ? String(v.price) : "",
    place: v.place ?? "", note: v.note ?? "",
  });

  function saver(path: string, method: "POST" | "PUT") {
    return async (d: Draft): Promise<string | null> => {
      try {
        await api(path, { method, json: {
          items: d.items, other: d.other.trim() || null, km: d.km ? Number(d.km) : null, done_on: d.date || null,
          price: d.price ? Number(d.price) : null, place: d.place.trim() || null, note: d.note.trim() || null,
        } });
        setOpen(null);
        load();
        onChange();
        return null;
      } catch (e) {
        return e instanceof ApiError && e.message ? e.message : t("common.error");
      }
    };
  }
  const create = saver(`/me/vehicles/${car.id}/maintenance`, "POST");

  async function removeVisit(v: Visit) {
    if (!window.confirm(t("carnet.remove.confirm"))) return;
    await api(`/me/vehicles/${car.id}/maintenance/visits/${v.id}`, { method: "DELETE" }).catch(() => undefined);
    load();
    onChange();
  }

  if (!items) return <p>{t("common.loading")}</p>;
  return (
    <div className="maintenance">
      {car.mileage_km == null && <p className="notice">{t("maint.noMileage")}</p>}
      <ul className="list">
        {items.map((it) => (
          <li key={it.item} className={`maint is-${it.status}`}>
            <div style={{ width: "100%" }}>
              <div className="status-head">
                <strong>{it.name}</strong>
                <span className={`maint-pill is-${it.status}`}>{t(`maint.status.${it.status}`)}</span>
              </div>
              <span className="meta">
                {it.status === "check" ? t("maint.check")
                  : [it.next_km != null && t("maint.nextKm", { km: km(it.next_km) }) + (it.km_left != null ? ` (${it.km_left > 0 ? t("maint.in", { km: km(it.km_left) }) : t("maint.over", { km: km(-it.km_left) })})` : ""),
                     it.next_date && t("maint.nextDate", { date: day(it.next_date) })].filter(Boolean).join(t("maint.or"))}
              </span>
              <br />
              <span className="meta">
                {it.last ? t("maint.last", { date: day(it.last.done_on), km: it.last.km != null ? ` à ${km(it.last.km)}` : "" })
                  : t("maint.every", { km: km(it.every_km), months: it.every_months })}
              </span>
              {open === it.item ? (
                <>
                  <p className="help">{it.why}</p>
                  <VisitForm all={items} draft={blank([it.item])} onSave={create} onCancel={() => setOpen(null)} saveLabel={t("maint.save")} />
                </>
              ) : (
                <div className="actions" style={{ marginTop: "0.4rem" }}>
                  <button type="button" className="btn btn-ghost" onClick={() => setOpen(it.item)}
                    aria-label={t("maint.doneFor", { name: it.name })}>{t("maint.done")}</button>
                  {it.part && (it.status === "due" || it.status === "soon" || it.status === "check") && (
                    <Link className="btn btn-ghost" href={`/magasins?${new URLSearchParams({ category: String(it.part.category_id),
                      part: it.part.name, ...(car.variant_id ? { variant: String(car.variant_id) } : {}) })}`}>
                      {t("maint.shops")}
                    </Link>
                  )}
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
      <p className="help">{t("maint.disclaimer")}</p>

      {/* Carnet d'entretien : chaque passage au garage, du plus récent au plus ancien */}
      <section className="carnet" aria-labelledby={`carnet-${car.id}`}>
        <div className="status-head">
          <h3 id={`carnet-${car.id}`} className="card-title" style={{ margin: 0 }}>{t("carnet.title")}</h3>
          {open !== "new" && <button type="button" className="btn btn-ghost" onClick={() => setOpen("new")}>{t("carnet.add")}</button>}
        </div>
        {open === "new" && <VisitForm all={items} draft={blank([])} onSave={create} onCancel={() => setOpen(null)} saveLabel={t("carnet.save")} />}
        {history && history.priced > 0 && (
          <p className="carnet-total">
            <strong>{da(history.total_12_months)}</strong> {t("carnet.total12")}
            {history.total !== history.total_12_months && <span className="meta"> · {t("carnet.totalAll", { total: da(history.total) })}</span>}
          </p>
        )}
        {history && history.visits.length === 0 && open !== "new" && <p className="help">{t("carnet.empty")}</p>}
        {history && history.visits.length > 0 && (
          <ol className="carnet-list">
            {history.visits.map((v) => (
              <li key={v.id} className="visit">
                {open === v.id ? (
                  <VisitForm all={items} draft={fromVisit(v)} saveLabel={t("carnet.update")} onCancel={() => setOpen(null)}
                    onSave={saver(`/me/vehicles/${car.id}/maintenance/visits/${v.id}`, "PUT")} />
                ) : (
                  <>
                    <div className="status-head">
                      <strong>{day(v.done_on)}{v.km != null ? ` · ${km(v.km)}` : ""}</strong>
                      {v.price != null && <span className="visit-price">{da(v.price)}</span>}
                    </div>
                    <span>{v.operations.map((o) => o.name).join(", ")}</span>
                    {(v.place || v.note) && <span className="meta">{[v.place, v.note].filter(Boolean).join(" · ")}</span>}
                    <div className="actions" style={{ marginTop: "0.3rem" }}>
                      <button type="button" className="chip" onClick={() => setOpen(v.id)}
                        aria-label={t("carnet.editFor", { date: day(v.done_on) })}>{t("carnet.edit")}</button>
                      <button type="button" className="chip" onClick={() => removeVisit(v)}
                        aria-label={t("carnet.removeFor", { date: day(v.done_on) })}>{t("carnet.remove")}</button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
