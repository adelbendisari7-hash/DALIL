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

const km = (n: number) => `${n.toLocaleString("fr-FR")} km`;
const day = (iso: string) => new Date(iso).toLocaleDateString("fr-FR");

/** Prochains entretiens d'une voiture : à faire, bientôt, à vérifier ; « Fait » note l'entretien (aujourd'hui, au
 * kilométrage actuel par défaut) ; lien direct vers les magasins qui vendent la pièce. Intervalles indicatifs. */
export default function Maintenance({ car, onChange }: { car: UserCar; onChange: () => void }) {
  const [items, setItems] = useState<Item[] | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  const [form, setForm] = useState({ km: "", date: "" });
  const [msg, setMsg] = useState("");

  const load = useCallback(() => {
    api<{ items: Item[] }>(`/me/vehicles/${car.id}/maintenance`).then((r) => setItems(r.items)).catch(() => setItems([]));
  }, [car.id]);
  useEffect(() => { load(); }, [load]);

  function startDone(it: Item) {
    setOpen(it.item);
    setForm({ km: car.mileage_km != null ? String(car.mileage_km) : "", date: new Date().toISOString().slice(0, 10) });
  }

  async function done(it: Item) {
    setMsg("");
    try {
      await api(`/me/vehicles/${car.id}/maintenance`, { method: "POST",
        json: { item: it.item, km: form.km ? Number(form.km) : null, done_on: form.date || null } });
      setOpen(null);
      load();
      onChange();
    } catch (e) {
      setMsg(e instanceof ApiError && e.message ? e.message : t("common.error"));
    }
  }

  async function undo(it: Item) {
    if (!it.last) return;
    await api(`/me/vehicles/${car.id}/maintenance/${it.last.id}`, { method: "DELETE" }).catch(() => undefined);
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
                <div className="car-form">
                  <p className="help" style={{ marginTop: 0 }}>{it.why}</p>
                  <div className="row">
                    <div>
                      <label htmlFor={`m-km-${it.item}`}>{t("account.cars.mileage")}</label>
                      <input id={`m-km-${it.item}`} inputMode="numeric" value={form.km} onChange={(e) => setForm({ ...form, km: e.target.value.replace(/\D/g, "") })} />
                    </div>
                    <div>
                      <label htmlFor={`m-date-${it.item}`}>{t("maint.date")}</label>
                      <input id={`m-date-${it.item}`} type="date" value={form.date} max={new Date().toISOString().slice(0, 10)}
                        onChange={(e) => setForm({ ...form, date: e.target.value })} />
                    </div>
                  </div>
                  {msg && <p className="err" role="alert">{msg}</p>}
                  <div className="actions">
                    <button type="button" className="btn" onClick={() => done(it)}>{t("maint.save")}</button>
                    <button type="button" className="btn btn-ghost" onClick={() => setOpen(null)}>{t("account.cars.cancel")}</button>
                  </div>
                </div>
              ) : (
                <div className="actions" style={{ marginTop: "0.4rem" }}>
                  <button type="button" className="btn btn-ghost" onClick={() => startDone(it)}
                    aria-label={t("maint.doneFor", { name: it.name })}>{t("maint.done")}</button>
                  {it.part && (it.status === "due" || it.status === "soon" || it.status === "check") && (
                    <Link className="btn btn-ghost" href={`/magasins?${new URLSearchParams({ category: String(it.part.category_id),
                      part: it.part.name, ...(car.variant_id ? { variant: String(car.variant_id) } : {}) })}`}>
                      {t("maint.shops")}
                    </Link>
                  )}
                  {it.last && <button type="button" className="chip" onClick={() => undo(it)}>{t("maint.undo")}</button>}
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
      <p className="help">{t("maint.disclaimer")}</p>
    </div>
  );
}
