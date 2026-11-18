"use client";
import { useEffect, useRef, useState } from "react";
import { api, vehicleStore, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

type Brand = { id: number; name: string };
type Model = { id: number; name: string };
type Variant = { id: number; engine: string; fuel: string; year_from: number; year_to: number | null; label: string };
type Hit = { brand_id: number; brand: string; model_id: number; model: string };
const OTHER_ENGINE = "Autre motorisation";

const THIS_YEAR = new Date().getFullYear();

/** Années où le modèle existe (réunion des périodes de ses motorisations), de la plus récente à la plus ancienne. */
function modelYears(vs: Variant[]): number[] {
  const years = new Set<number>();
  for (const v of vs) for (let y = v.year_from; y <= (v.year_to ?? THIS_YEAR); y++) years.add(y);
  return Array.from(years).sort((a, b) => b - a);
}

/** Sélection du véhicule (F1) : marque, modèle, année, motorisation. Mémorisé sur l'appareil. */
export default function VehiclePicker({ onChange }: { onChange: (v: Vehicle | null) => void }) {
  const [saved, setSaved] = useState<Vehicle | null>(null);
  const [editing, setEditing] = useState(false);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [modelVariants, setModelVariants] = useState<Variant[]>([]);
  const [brand, setBrand] = useState<Brand | null>(null);
  const [model, setModel] = useState<Model | null>(null);
  const [year, setYear] = useState<number | "">("");
  // Recherche par saisie (« clio 2 ») : choisit la marque puis le modèle une fois la liste des modèles chargée
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const pendingModel = useRef<number | null>(null);
  // « Mon véhicule n'est pas dans la liste »
  const [missingOpen, setMissingOpen] = useState(false);
  const [missing, setMissing] = useState({ brand: "", model: "", year: "", engine: "" });
  const [missingSent, setMissingSent] = useState(false);

  useEffect(() => {
    const v = vehicleStore.get();
    setSaved(v);
    setEditing(!v);
    onChange(v);
    api<Brand[]>("/vehicles/brands").then(setBrands).catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setModels([]);
    setModel(null);
    if (!brand) return;
    api<Model[]>(`/vehicles/models?brand_id=${brand.id}`)
      .then((ms) => {
        setModels(ms);
        const wanted = ms.find((m) => m.id === pendingModel.current);
        pendingModel.current = null;
        if (wanted) setModel(wanted);
      })
      .catch(() => undefined);
  }, [brand]);

  useEffect(() => {
    if (query.trim().length < 2) return setHits([]);
    const id = setTimeout(() => {
      api<Hit[]>(`/vehicles/search?q=${encodeURIComponent(query.trim())}`).then(setHits).catch(() => setHits([]));
    }, 200);
    return () => clearTimeout(id);
  }, [query]);

  function pick(h: Hit) {
    const b = brands.find((x) => x.id === h.brand_id);
    if (!b) return;
    if (brand?.id === b.id) {
      // Même marque : la liste des modèles est déjà chargée
      const m = models.find((x) => x.id === h.model_id);
      if (m) setModel(m);
    } else {
      pendingModel.current = h.model_id;
      setBrand(b);
    }
    setQuery("");
    setHits([]);
  }

  async function sendMissing(e: React.FormEvent) {
    e.preventDefault();
    if (!missing.brand.trim() || !missing.model.trim()) return;
    await api("/vehicles/requests", {
      method: "POST",
      json: { brand: missing.brand.trim(), model: missing.model.trim(), year: missing.year ? +missing.year : null,
              engine: missing.engine.trim() || null },
    }).catch(() => undefined);
    setMissingSent(true);
  }

  // Toutes les motorisations du modèle : elles bornent la liste des années (pas de « Tiggo 4 de 2010 »).
  useEffect(() => {
    setModelVariants([]);
    setYear("");
    if (model) api<Variant[]>(`/vehicles/variants?model_id=${model.id}`).then(setModelVariants).catch(() => undefined);
  }, [model]);

  useEffect(() => {
    setVariants([]);
    if (!model) return;
    const q = year ? `&year=${year}` : "";
    api<Variant[]>(`/vehicles/variants?model_id=${model.id}${q}`)
      .then((vs) => {
        setVariants(vs);
        if (vs.length === 1 && year) choose(vs[0]);
      })
      .catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [model, year]);

  function choose(v: Variant) {
    if (!brand || !model) return;
    const veh: Vehicle = {
      variantId: v.id,
      brand: brand.name,
      model: model.name,
      label: `${brand.name} ${model.name}${v.engine === OTHER_ENGINE ? "" : ` ${v.engine}`}${year ? ` ${year}` : ""}`,
    };
    vehicleStore.set(veh);
    setSaved(veh);
    setEditing(false);
    onChange(veh);
  }

  if (!editing && saved) {
    return (
      <div className="vehicle-line">
        <div>
          <span className="meta">{t("vehicle.title")}</span>
          <br />
          <strong>{saved.label}</strong>
        </div>
        <button type="button" className="btn btn-ghost" onClick={() => setEditing(true)}>
          {t("vehicle.change")}
        </button>
      </div>
    );
  }

  return (
    <fieldset style={{ border: 0, padding: 0, margin: "1.25rem 0 0" }}>
      <legend style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "var(--step-1)" }}>
        {t("vehicle.title")}
      </legend>
      <label htmlFor="v-search">{t("vehicle.search")}</label>
      <input id="v-search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("vehicle.search.placeholder")}
             autoComplete="off" />
      {hits.length > 0 && (
        <div className="chips" role="listbox" aria-label={t("vehicle.search")}>
          {hits.map((h) => (
            <button type="button" key={h.model_id} className="chip" role="option" aria-selected={false} onClick={() => pick(h)}>
              {h.brand} {h.model}
            </button>
          ))}
        </div>
      )}
      <div className="row">
        <div>
          <label htmlFor="v-brand">{t("vehicle.brand")}</label>
          <select id="v-brand" value={brand?.id ?? ""} onChange={(e) => setBrand(brands.find((b) => b.id === +e.target.value) ?? null)}>
            <option value="">{t("vehicle.choose")}</option>
            {brands.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="v-model">{t("vehicle.model")}</label>
          <select id="v-model" disabled={!brand} value={model?.id ?? ""} onChange={(e) => setModel(models.find((m) => m.id === +e.target.value) ?? null)}>
            <option value="">{t("vehicle.choose")}</option>
            {models.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="v-year">{t("vehicle.year")}</label>
          <select id="v-year" disabled={!model} value={year} onChange={(e) => setYear(e.target.value ? +e.target.value : "")}>
            <option value="">{t("vehicle.choose")}</option>
            {modelYears(modelVariants).map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="v-engine">{t("vehicle.engine")}</label>
          <select
            id="v-engine"
            disabled={!variants.length}
            value=""
            onChange={(e) => {
              const v = variants.find((x) => x.id === +e.target.value);
              if (v) choose(v);
            }}
          >
            <option value="">{t("vehicle.choose")}</option>
            {variants.map((v) => (
              <option key={v.id} value={v.id}>{v.label}</option>
            ))}
          </select>
        </div>
      </div>
      <p className="help">{t("vehicle.none")}</p>
      {!missingOpen ? (
        <button type="button" className="btn btn-ghost" onClick={() => setMissingOpen(true)}>{t("vehicle.missing.open")}</button>
      ) : missingSent ? (
        <p className="ok" role="status">{t("vehicle.missing.thanks")}</p>
      ) : (
        <div className="questions">
          <p className="help">{t("vehicle.missing.help")}</p>
          <div className="row">
            <div><label htmlFor="m-brand">{t("vehicle.brand")}</label>
              <input id="m-brand" value={missing.brand} maxLength={60} onChange={(e) => setMissing({ ...missing, brand: e.target.value })} /></div>
            <div><label htmlFor="m-model">{t("vehicle.model")}</label>
              <input id="m-model" value={missing.model} maxLength={80} onChange={(e) => setMissing({ ...missing, model: e.target.value })} /></div>
            <div><label htmlFor="m-year">{t("vehicle.year")}</label>
              <input id="m-year" inputMode="numeric" maxLength={4} value={missing.year}
                     onChange={(e) => setMissing({ ...missing, year: e.target.value.replace(/\D/g, "") })} /></div>
            <div><label htmlFor="m-engine">{t("vehicle.engine")}</label>
              <input id="m-engine" value={missing.engine} maxLength={60} placeholder="1.9 D, 2.5 diesel…"
                     onChange={(e) => setMissing({ ...missing, engine: e.target.value })} /></div>
          </div>
          <div className="actions"><button type="button" className="btn" onClick={sendMissing}>{t("vehicle.missing.send")}</button></div>
        </div>
      )}
    </fieldset>
  );
}
