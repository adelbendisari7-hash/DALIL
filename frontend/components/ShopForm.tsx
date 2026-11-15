"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Named = { id: number; name: string };
type Commune = { id: number; nom_fr: string };

export type ShopFormValue = {
  name: string; phone: string; whatsapp: string; commune_id: number | null; lat: number | null; lng: number | null;
  address: string; hours: string; brand_ids: number[]; category_ids: number[];
  parts_origin: string[]; sale_mode: string | null; survey?: Record<string, string>;
};

export const emptyShop: ShopFormValue = {
  name: "", phone: "", whatsapp: "", commune_id: null, lat: null, lng: null, address: "", hours: "",
  brand_ids: [], category_ids: [], parts_origin: [], sale_mode: null,
};

function toggle(list: number[] | string[], v: number | string) {
  const l = list as (number | string)[];
  return (l.includes(v) ? l.filter((x) => x !== v) : [...l, v]) as typeof list;
}

/** Fiche magasin : inscription en libre-service (< 3 min) et fiche de visite terrain (avec étude de marché). */
export default function ShopForm({
  initial, field = false, showPhone = true, submitLabel, onSubmit,
}: {
  initial?: Partial<ShopFormValue>; field?: boolean; showPhone?: boolean; submitLabel: string;
  onSubmit: (v: ShopFormValue) => Promise<void>;
}) {
  const [v, setV] = useState<ShopFormValue>(() => {
    const base = { ...emptyShop, ...initial } as ShopFormValue;
    for (const k of ["name", "phone", "whatsapp", "address", "hours"] as const) base[k] = base[k] ?? "";
    base.parts_origin = base.parts_origin ?? [];
    return base;
  });
  const [brands, setBrands] = useState<Named[]>([]);
  const [families, setFamilies] = useState<Named[]>([]);
  const [communes, setCommunes] = useState<Commune[]>([]);
  const [busy, setBusy] = useState(false);
  const [geoMsg, setGeoMsg] = useState("");

  useEffect(() => {
    api<Named[]>("/vehicles/brands").then(setBrands).catch(() => undefined);
    api<Named[]>("/parts/categories").then(setFamilies).catch(() => undefined);
    api<Commune[]>("/geo/communes").then(setCommunes).catch(() => undefined);
  }, []);

  const set = <K extends keyof ShopFormValue>(k: K, val: ShopFormValue[K]) => setV((p) => ({ ...p, [k]: val }));
  const survey = (k: string, val: string) => setV((p) => ({ ...p, survey: { ...(p.survey || {}), [k]: val } }));

  function here() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (p) => { set("lat", +p.coords.latitude.toFixed(6)); set("lng", +p.coords.longitude.toFixed(6)); setGeoMsg(t("shop.position.ok")); },
      () => setGeoMsg(t("shops.locate.denied")),
      { enableHighAccuracy: true, timeout: 15000 }
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try { await onSubmit(v); } finally { setBusy(false); }
  }

  return (
    <form onSubmit={submit}>
      <label htmlFor="s-name">{t("shop.name")}</label>
      <input id="s-name" value={v.name} onChange={(e) => set("name", e.target.value)} required minLength={2} />
      {showPhone && (
        <>
          <label htmlFor="s-phone">{t("login.phone")}</label>
          <input id="s-phone" type="tel" inputMode="tel" value={v.phone} onChange={(e) => set("phone", e.target.value)} />
        </>
      )}
      <label htmlFor="s-wa">{t("shop.whatsapp")}</label>
      <input id="s-wa" type="tel" inputMode="tel" value={v.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} />
      <div className="row">
        <div>
          <label htmlFor="s-commune">{t("shop.commune")}</label>
          <select id="s-commune" value={v.commune_id ?? ""} onChange={(e) => set("commune_id", e.target.value ? +e.target.value : null)}>
            <option value="">{t("vehicle.choose")}</option>
            {communes.map((c) => <option key={c.id} value={c.id}>{c.nom_fr}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="s-hours">{t("shop.hours")}</label>
          <input id="s-hours" placeholder="Sam-Jeu 8h-18h" value={v.hours} onChange={(e) => set("hours", e.target.value)} />
        </div>
      </div>
      <label htmlFor="s-addr">{t("shops.address")}</label>
      <input id="s-addr" value={v.address} onChange={(e) => set("address", e.target.value)} />

      <label>{t("shop.position")}</label>
      <button type="button" className="btn btn-ghost" onClick={here}>{t("shop.position.here")}</button>
      <p className="help" role="status">{geoMsg || (v.lat ? `${v.lat}, ${v.lng}` : "")}</p>

      <label>{t("shop.brands")}</label>
      <div className="chips">
        {brands.map((b) => (
          <button type="button" key={b.id} className="chip" aria-pressed={v.brand_ids.includes(b.id)} onClick={() => set("brand_ids", toggle(v.brand_ids, b.id) as number[])}>{b.name}</button>
        ))}
      </div>
      <label>{t("shop.categories")}</label>
      <div className="chips">
        {families.map((f) => (
          <button type="button" key={f.id} className="chip" aria-pressed={v.category_ids.includes(f.id)} onClick={() => set("category_ids", toggle(v.category_ids, f.id) as number[])}>{f.name}</button>
        ))}
      </div>

      <label>{t("field.origin")}</label>
      <div className="chips">
        {["origine", "adaptable", "occasion"].map((o) => (
          <button type="button" key={o} className="chip" aria-pressed={v.parts_origin.includes(o)} onClick={() => set("parts_origin", toggle(v.parts_origin, o) as string[])}>{t(`shop.condition.${o}`)}</button>
        ))}
      </div>
      <label>{t("field.saleMode")}</label>
      <div className="chips">
        {["detail", "gros", "les_deux"].map((o) => (
          <button type="button" key={o} className="chip" aria-pressed={v.sale_mode === o} onClick={() => set("sale_mode", o)}>{t(`field.saleMode.${o}`)}</button>
        ))}
      </div>

      {field && (
        <fieldset style={{ border: 0, padding: 0, marginTop: "1.5rem" }}>
          <label htmlFor="sv-top">{t("field.survey.top")}</label>
          <textarea id="sv-top" style={{ minHeight: "4rem" }} onChange={(e) => survey("modeles_demandes", e.target.value)} />
          <div className="row">
            <div>
              <label htmlFor="sv-day">{t("field.survey.perDay")}</label>
              <input id="sv-day" inputMode="numeric" onChange={(e) => survey("demandes_par_jour", e.target.value)} />
            </div>
            <div>
              <label htmlFor="sv-pay">{t("field.survey.pay")}</label>
              <select id="sv-pay" onChange={(e) => survey("pret_a_payer", e.target.value)}>
                <option value="">{t("vehicle.choose")}</option>
                <option value="oui">{t("common.yes")}</option>
                <option value="non">{t("common.no")}</option>
              </select>
            </div>
          </div>
          <label htmlFor="sv-how">{t("field.survey.how")}</label>
          <input id="sv-how" onChange={(e) => survey("comment_trouve", e.target.value)} />
        </fieldset>
      )}

      <div className="actions"><button className="btn btn-primary btn-block" disabled={busy}>{submitLabel}</button></div>
    </form>
  );
}

export function cleanShop(v: ShopFormValue) {
  return {
    ...v,
    phone: v.phone || null, whatsapp: v.whatsapp || null, address: v.address || null, hours: v.hours || null,
  };
}
