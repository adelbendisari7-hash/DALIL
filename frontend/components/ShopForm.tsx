"use client";
import { useEffect, useState } from "react";
import HoursPicker, { cleanOpening, DEFAULT_OPENING, type Opening } from "@/components/HoursPicker";
import PinMap from "@/components/PinMap";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Named = { id: number; name: string };

export type ShopFormValue = {
  name: string; phone: string; whatsapp: string; commune_id: number | null; lat: number | null; lng: number | null;
  address: string; landmark: string; hours: string; opening: Opening | null; brand_ids: number[]; category_ids: number[];
  parts_origin: string[]; sale_mode: string | null; survey?: Record<string, string>;
};

export const emptyShop: ShopFormValue = {
  name: "", phone: "", whatsapp: "", commune_id: null, lat: null, lng: null, address: "", landmark: "", hours: "",
  opening: DEFAULT_OPENING, brand_ids: [], category_ids: [], parts_origin: [], sale_mode: null,
};

// Raccourcis « ce que vous vendez » (noms du référentiel ; ceux qui n'existent pas sont ignorés)
const FRENCH_BRANDS = ["Renault", "Peugeot", "Citroën", "Dacia"];

function toggle<T>(list: T[], v: T): T[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}

export function normalizeShop(initial?: Partial<ShopFormValue>): ShopFormValue {
  const base = { ...emptyShop, ...initial } as ShopFormValue;
  for (const k of ["name", "phone", "whatsapp", "address", "hours", "landmark"] as const) base[k] = base[k] ?? "";
  base.parts_origin = base.parts_origin ?? [];
  base.opening = initial && "opening" in initial ? (initial.opening ?? null) : DEFAULT_OPENING;
  return base;
}

type Section = { v: ShopFormValue; set: <K extends keyof ShopFormValue>(k: K, val: ShopFormValue[K]) => void };

/** Nom, téléphones, horaires. */
export function IdentityFields({ v, set, showPhone }: Section & { showPhone: boolean }) {
  return (
    <>
      <label htmlFor="s-name">{t("shop.name")}</label>
      <input id="s-name" value={v.name} onChange={(e) => set("name", e.target.value)} required minLength={2} maxLength={160} />
      {showPhone && (
        <>
          <label htmlFor="s-phone">{t("shop.phone")}</label>
          <input id="s-phone" type="tel" inputMode="tel" placeholder={t("login.phone.placeholder")} value={v.phone} onChange={(e) => set("phone", e.target.value)} />
          <p className="help">{t("shop.phone.help")}</p>
        </>
      )}
      <label htmlFor="s-wa">{t("shop.whatsapp")}</label>
      <input id="s-wa" type="tel" inputMode="tel" value={v.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} />
      <label>{t("shop.hours")}</label>
      {v.opening ? (
        <HoursPicker value={v.opening} onChange={(o) => set("opening", o)} />
      ) : (
        <>
          <p className="help">{v.hours || t("shop.hours.unknown")}</p>
          <button type="button" className="btn btn-ghost" onClick={() => set("opening", DEFAULT_OPENING)}>{t("shop.hours.set")}</button>
        </>
      )}
    </>
  );
}

/** Adresse et épingle sur la carte, repère. */
export function LocationFields({ v, set }: Section) {
  return (
    <>
      <PinMap
        value={v.lat != null && v.lng != null ? { lat: v.lat, lng: v.lng } : null}
        onChange={(p) => { set("lat", p.lat); set("lng", p.lng); }}
        address={v.address}
        onAddress={(a) => set("address", a)}
      />
      <label htmlFor="s-landmark">{t("shop.landmark")} <span className="meta">({t("account.optional")})</span></label>
      <input id="s-landmark" maxLength={200} placeholder={t("shop.landmark.placeholder")} value={v.landmark} onChange={(e) => set("landmark", e.target.value)} />
    </>
  );
}

/** Marques, familles, origine des pièces, gros ou détail, avec des raccourcis. */
export function SellsFields({ v, set }: Section) {
  const [brands, setBrands] = useState<Named[]>([]);
  const [families, setFamilies] = useState<Named[]>([]);
  useEffect(() => {
    api<Named[]>("/vehicles/brands").then(setBrands).catch(() => undefined);
    api<Named[]>("/parts/categories").then(setFamilies).catch(() => undefined);
  }, []);
  const french = brands.filter((b) => FRENCH_BRANDS.includes(b.name)).map((b) => b.id);
  const addAll = (ids: number[], current: number[]) => Array.from(new Set([...current, ...ids]));

  return (
    <>
      <label>{t("shop.brands")}</label>
      <div className="chips shortcuts">
        <button type="button" className="chip chip-shortcut" onClick={() => set("brand_ids", addAll(french, v.brand_ids))}>+ {t("shop.brands.french")}</button>
        <button type="button" className="chip chip-shortcut" onClick={() => set("brand_ids", brands.map((b) => b.id))}>+ {t("shop.all")}</button>
        {v.brand_ids.length > 0 && <button type="button" className="chip chip-shortcut" onClick={() => set("brand_ids", [])}>{t("shop.none")}</button>}
      </div>
      <div className="chips">
        {brands.map((b) => (
          <button type="button" key={b.id} className="chip" aria-pressed={v.brand_ids.includes(b.id)} onClick={() => set("brand_ids", toggle(v.brand_ids, b.id))}>{b.name}</button>
        ))}
      </div>
      <label>{t("shop.categories")}</label>
      <div className="chips shortcuts">
        <button type="button" className="chip chip-shortcut" onClick={() => set("category_ids", families.map((f) => f.id))}>+ {t("shop.all")}</button>
        {v.category_ids.length > 0 && <button type="button" className="chip chip-shortcut" onClick={() => set("category_ids", [])}>{t("shop.none")}</button>}
      </div>
      <div className="chips">
        {families.map((f) => (
          <button type="button" key={f.id} className="chip" aria-pressed={v.category_ids.includes(f.id)} onClick={() => set("category_ids", toggle(v.category_ids, f.id))}>{f.name}</button>
        ))}
      </div>
      <label>{t("field.origin")}</label>
      <div className="chips">
        {["origine", "adaptable", "occasion"].map((o) => (
          <button type="button" key={o} className="chip" aria-pressed={v.parts_origin.includes(o)} onClick={() => set("parts_origin", toggle(v.parts_origin, o))}>{t(`shop.condition.${o}`)}</button>
        ))}
      </div>
      <label>{t("field.saleMode")}</label>
      <div className="chips">
        {["detail", "gros", "les_deux"].map((o) => (
          <button type="button" key={o} className="chip" aria-pressed={v.sale_mode === o} onClick={() => set("sale_mode", o)}>{t(`field.saleMode.${o}`)}</button>
        ))}
      </div>
    </>
  );
}

/** Fiche magasin sur une page (modification de sa fiche, fiche de visite terrain avec étude de marché).
 * L'inscription en libre-service passe par les étapes de ShopWizard, avec les mêmes blocs. */
export default function ShopForm({
  initial, field = false, showPhone = true, submitLabel, onSubmit,
}: {
  initial?: Partial<ShopFormValue>; field?: boolean; showPhone?: boolean; submitLabel: string;
  onSubmit: (v: ShopFormValue) => Promise<void>;
}) {
  const [v, setV] = useState<ShopFormValue>(() => normalizeShop(initial));
  const [busy, setBusy] = useState(false);
  const set = <K extends keyof ShopFormValue>(k: K, val: ShopFormValue[K]) => setV((p) => ({ ...p, [k]: val }));
  const survey = (k: string, val: string) => setV((p) => ({ ...p, survey: { ...(p.survey || {}), [k]: val } }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try { await onSubmit(v); } finally { setBusy(false); }
  }

  return (
    <form onSubmit={submit}>
      <IdentityFields v={v} set={set} showPhone={showPhone} />
      <LocationFields v={v} set={set} />
      <SellsFields v={v} set={set} />

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

/** Pour l'API : champs vides retirés ; avec des horaires structurés, le texte est recalculé par le serveur. */
export function cleanShop(v: ShopFormValue) {
  // commune déduite de la position par le serveur : on ne l'envoie que si elle est connue
  const { opening, hours, commune_id, ...rest } = v;
  return {
    ...rest,
    ...(commune_id ? { commune_id } : {}),
    phone: v.phone || null, whatsapp: v.whatsapp || null, address: v.address || null, landmark: v.landmark || null,
    ...(opening ? { opening: cleanOpening(opening) } : { hours: hours || null }),
  };
}
