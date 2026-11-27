"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import { API, api, ApiError, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";
import { daysAgo, photoForm, shrinkPhoto } from "@/lib/photo";

type Family = { id: number; name: string; children: { id: number; slug: string; name: string }[] };
const COMMON = ["plaquettes-avant", "disques-frein", "filtre-huile", "filtre-air", "bougies-allumage", "amortisseurs", "kit-embrayage", "batterie"];
export type Product = {
  id: number; title: string; oem_ref: string | null; price: number | null; condition: string; category_id: number;
  in_stock: boolean; photo_url: string | null; price_confirmed_at: string | null; variant_ids: number[];
};
type ImportReport = { created: number; updated: number; errors: { line: number; error: string }[]; total: number };

const CONDITIONS = ["neuf", "origine", "adaptable", "occasion"];
const errMsg = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));
const OLD_PRICE_DAYS = 60;

/** Ajout d'un produit en moins de 30 s : famille en pastilles (les plus utilisées d'abord), titre proposé,
 * véhicules compatibles, prix, état, photo ; « Ajouter et continuer » garde la famille et les véhicules. */
function QuickAdd({ shopId, families, products, onAdded }: {
  shopId: number; families: Family[]; products: Product[]; onAdded: () => void;
}) {
  const cats = useMemo(() => families.flatMap((f) => f.children), [families]);
  const frequent = useMemo(() => {
    const n = new Map<number, number>();
    products.forEach((p) => n.set(p.category_id, (n.get(p.category_id) ?? 0) + 1));
    const used = [...n.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
    // Familles déjà utilisées par le magasin d'abord, complétées par les pièces d'usure les plus vendues
    const common = cats.filter((c) => COMMON.includes(c.slug) && !used.includes(c.id)).map((c) => c.id);
    return [...used, ...common].slice(0, 8);
  }, [products, cats]);
  const [cat, setCat] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [ref, setRef] = useState("");
  const [condition, setCondition] = useState("adaptable");
  const [inStock, setInStock] = useState(true);
  const [fits, setFits] = useState<Vehicle[]>([]);
  const [picking, setPicking] = useState(false);
  const [photo, setPhoto] = useState<Blob | null>(null);
  const [preview, setPreview] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const titleTouched = useRef(false);
  const catName = (id: number | null) => cats.find((c) => c.id === id)?.name ?? "";

  function chooseCat(id: number) {
    setCat(id);
    if (!titleTouched.current) setTitle(catName(id));   // titre proposé d'après la famille
  }

  async function takePhoto(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    try {
      const b = await shrinkPhoto(f);
      setPhoto(b);
      setPreview(URL.createObjectURL(b));
    } catch {
      setMsg({ ok: false, text: t("shop.photo.unreadable") });
    }
  }

  async function add(keep: boolean) {
    if (!cat || title.trim().length < 2) return setMsg({ ok: false, text: t("shop.quick.need") });
    setBusy(true);
    setMsg(null);
    try {
      const r = await api<{ id: number }>(`/shops/${shopId}/products`, {
        method: "POST",
        json: { title: title.trim(), category_id: cat, oem_ref: ref.trim() || null, price: price ? Number(price) : null,
                condition, in_stock: inStock, variant_ids: fits.map((v) => v.variantId) },
      });
      if (photo) await api(`/shops/${shopId}/products/${r.id}/photo`, { method: "POST", body: photoForm(photo) });
      setMsg({ ok: true, text: t("shop.product.added") });
      setTitle(keep ? catName(cat) : "");
      titleTouched.current = false;
      setPrice("");
      setRef("");
      setPhoto(null);
      setPreview("");
      if (!keep) { setCat(null); setFits([]); }
      onAdded();
    } catch (e) {
      setMsg({ ok: false, text: errMsg(e) });
    }
    setBusy(false);
  }

  return (
    <div className="card">
      <h2 className="card-title">{t("shop.quick.title")}</h2>
      <span className="help">{t("shop.product.category")}</span>
      <div className="chips">
        {frequent.map((id) => (
          <button key={id} type="button" className="chip" aria-pressed={cat === id} onClick={() => chooseCat(id)}>{catName(id)}</button>
        ))}
      </div>
      <label htmlFor="q-cat">{t("shop.quick.otherFamily")}</label>
      <select id="q-cat" value={cat ?? ""} onChange={(e) => e.target.value && chooseCat(Number(e.target.value))}>
        <option value="">{t("vehicle.choose")}</option>
        {families.map((f) => (
          <optgroup key={f.id} label={f.name}>
            {f.children.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </optgroup>
        ))}
      </select>

      <label htmlFor="q-title">{t("shop.product.title")}</label>
      <input id="q-title" maxLength={200} value={title} onChange={(e) => { titleTouched.current = true; setTitle(e.target.value); }} />
      <div className="row">
        <div>
          <label htmlFor="q-price">{t("shop.product.price")}</label>
          <input id="q-price" inputMode="numeric" value={price} onChange={(e) => setPrice(e.target.value.replace(/\D/g, ""))} />
        </div>
        <div>
          <label htmlFor="q-ref">{t("shop.product.ref")}</label>
          <input id="q-ref" maxLength={60} value={ref} onChange={(e) => setRef(e.target.value)} />
        </div>
      </div>
      <span className="help">{t("shop.product.condition")}</span>
      <div className="chips">
        {CONDITIONS.map((c) => (
          <button key={c} type="button" className="chip" aria-pressed={condition === c} onClick={() => setCondition(c)}>{t(`shop.condition.${c}`)}</button>
        ))}
      </div>
      <label className="check">
        <input type="checkbox" checked={inStock} onChange={(e) => setInStock(e.target.checked)} />
        <span>{t("shop.quick.inStock")}</span>
      </label>

      <span className="help">{t("shop.product.fits")}</span>
      <div className="chips">
        {fits.map((v) => (
          <button key={v.variantId} type="button" className="chip" aria-pressed onClick={() => setFits(fits.filter((x) => x.variantId !== v.variantId))}
            aria-label={t("shop.quick.removeFit", { car: v.label })}>
            {v.label} ✕
          </button>
        ))}
        {!picking && <button type="button" className="chip chip-shortcut" onClick={() => setPicking(true)}>+ {t("shop.quick.addFit")}</button>}
      </div>
      {picking && (
        <div className="car-form">
          <VehiclePicker key={fits.length} remember={false} onChange={(v) => {
            if (v && !fits.some((x) => x.variantId === v.variantId)) setFits([...fits, v]);
            if (v) setPicking(false);
          }} />
          <div className="actions"><button type="button" className="btn btn-ghost" onClick={() => setPicking(false)}>{t("account.cars.cancel")}</button></div>
        </div>
      )}

      <div className="photo-row">
        {preview && <img src={preview} alt="" className="thumb" />}
        <label className="btn btn-ghost photo-button">
          {preview ? t("shop.photo.change") : t("shop.photo.add")}
          <input type="file" accept="image/*" capture="environment" onChange={takePhoto} hidden />
        </label>
      </div>

      {msg && <p className={msg.ok ? "ok" : "err"} role={msg.ok ? "status" : "alert"}>{msg.text}</p>}
      <div className="actions">
        <button type="button" className={`btn${busy ? " is-busy" : ""}`} disabled={busy} onClick={() => add(true)}>{t("shop.quick.addContinue")}</button>
        <button type="button" className="btn btn-ghost" disabled={busy} onClick={() => add(false)}>{t("shop.product.add")}</button>
      </div>
    </div>
  );
}

/** Une ligne du catalogue : prix modifiable, stock en un toucher, confirmation du prix, photo. */
function ProductRow({ shopId, p, catName, onChange }: { shopId: number; p: Product; catName: string; onChange: () => void }) {
  const [editing, setEditing] = useState(false);
  const [price, setPrice] = useState(p.price != null ? String(p.price) : "");
  const age = daysAgo(p.price_confirmed_at);
  const patch = async (json: Record<string, unknown>) => {
    await api(`/shops/${shopId}/products/${p.id}`, { method: "PATCH", json }).catch(() => undefined);
    setEditing(false);
    onChange();
  };
  async function photo(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    const b = await shrinkPhoto(f).catch(() => null);
    if (b) await api(`/shops/${shopId}/products/${p.id}/photo`, { method: "POST", body: photoForm(b) }).catch(() => undefined);
    onChange();
  }
  return (
    <li className={`product-row${p.in_stock ? "" : " is-out"}`}>
      <label className="thumb-slot" aria-label={t("shop.photo.add")}>
        {p.photo_url ? <img src={p.photo_url} alt="" className="thumb" /> : <span className="thumb thumb-empty">+</span>}
        <input type="file" accept="image/*" capture="environment" onChange={photo} hidden />
      </label>
      <div className="product-main">
        <strong>{p.title}</strong>
        <span className="meta">{catName}{p.oem_ref ? ` · réf. ${p.oem_ref}` : ""} · {t(`shop.condition.${p.condition}`)}</span>
        <span className={`meta${age != null && age > OLD_PRICE_DAYS ? " err" : ""}`}>
          {age == null ? "" : age === 0 ? t("shop.price.today") : t("shop.price.age", { n: age })}
        </span>
      </div>
      <div className="product-side">
        {editing ? (
          <span className="price-edit">
            <input aria-label={t("shop.product.price")} inputMode="numeric" value={price} autoFocus
              onChange={(e) => setPrice(e.target.value.replace(/\D/g, ""))} />
            <button type="button" className="btn" onClick={() => patch({ price: price ? Number(price) : null })}>OK</button>
          </span>
        ) : (
          <button type="button" className="price-tag" onClick={() => setEditing(true)} aria-label={t("shop.price.edit", { title: p.title })}>
            {p.price != null ? `${p.price.toLocaleString("fr-FR")} DA` : t("shop.price.none")}
          </button>
        )}
        <button type="button" className={`stock-toggle${p.in_stock ? " on" : ""}`} aria-pressed={p.in_stock}
          onClick={() => patch({ in_stock: !p.in_stock })}>
          {p.in_stock ? t("shop.stock.in") : t("shop.stock.out")}
        </button>
        {age != null && age > OLD_PRICE_DAYS && (
          <button type="button" className="chip" onClick={() => patch({ confirm: true })}>{t("shop.price.confirm")}</button>
        )}
        <button type="button" className="chip" onClick={async () => {
          if (!window.confirm(t("shop.product.delete.confirm"))) return;
          await api(`/shops/${shopId}/products/${p.id}`, { method: "DELETE" }).catch(() => undefined);
          onChange();
        }}>{t("shop.product.delete")}</button>
      </div>
    </li>
  );
}

/** Import Excel avec aperçu : le fichier est d'abord lu sans rien enregistrer, puis le magasin confirme. */
function ImportBox({ shopId, onDone }: { shopId: number; onDone: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportReport | null>(null);
  const [msg, setMsg] = useState("");
  const send = (f: File, dry: boolean) => {
    const fd = new FormData();
    fd.append("file", f);
    return api<ImportReport>(`/shops/${shopId}/products/import${dry ? "?dry_run=true" : ""}`, { method: "POST", body: fd });
  };
  async function choose(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    setMsg("");
    try {
      setFile(f);
      setPreview(await send(f, true));
    } catch (err) { setMsg(errMsg(err)); }
  }
  async function confirm() {
    if (!file) return;
    try {
      const r = await send(file, false);
      setMsg(t("shop.import.result", { created: r.created, updated: r.updated, errors: r.errors.length }));
      setPreview(null);
      setFile(null);
      onDone();
    } catch (err) { setMsg(errMsg(err)); }
  }
  return (
    <div className="card">
      <h2 className="card-title">{t("shop.import.title")}</h2>
      <p className="help" style={{ marginTop: 0 }}>{t("shop.import.help")}</p>
      <div className="actions">
        <a className="btn btn-ghost" href={`${API}/catalog/template.xlsx`} download>{t("shop.import.template")}</a>
        <label className="btn btn-ghost">
          {t("shop.import.choose")}
          <input type="file" accept=".xlsx,.csv" onChange={choose} hidden aria-label={t("shop.import.title")} />
        </label>
      </div>
      {preview && (
        <div className="car-form">
          <p><strong>{t("shop.import.preview", { created: preview.created, updated: preview.updated, errors: preview.errors.length })}</strong></p>
          {preview.errors.length > 0 && (
            <ul className="import-errors">
              {preview.errors.slice(0, 10).map((x) => <li key={x.line}>{t("shop.import.line", { n: x.line })} : {x.error}</li>)}
            </ul>
          )}
          <div className="actions">
            <button type="button" className="btn" disabled={!preview.created && !preview.updated} onClick={confirm}>
              {t("shop.import.confirm", { n: preview.created + preview.updated })}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => { setPreview(null); setFile(null); }}>{t("account.cars.cancel")}</button>
          </div>
        </div>
      )}
      {msg && <p className="help" role="status">{msg}</p>}
    </div>
  );
}

export default function ShopCatalog({ shopId, onCount }: { shopId: number; onCount?: (n: number) => void }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [families, setFamilies] = useState<Family[]>([]);
  const [q, setQ] = useState("");
  const [fam, setFam] = useState("");
  const load = useCallback(() => {
    api<Product[]>(`/shops/${shopId}/products`).then((ps) => { setProducts(ps); onCount?.(ps.length); }).catch(() => undefined);
  }, [shopId, onCount]);
  useEffect(() => {
    load();
    api<Family[]>("/parts/categories").then(setFamilies).catch(() => undefined);
  }, [load]);

  const cats = families.flatMap((f) => f.children.map((c) => ({ ...c, family: f.id })));
  const catName = (id: number) => cats.find((c) => c.id === id)?.name ?? "";
  const shown = products.filter((p) => {
    const famOk = !fam || cats.find((c) => c.id === p.category_id)?.family === Number(fam);
    const s = q.trim().toLowerCase();
    return famOk && (!s || p.title.toLowerCase().includes(s) || (p.oem_ref ?? "").toLowerCase().includes(s));
  });
  const old = products.filter((p) => (daysAgo(p.price_confirmed_at) ?? 0) > OLD_PRICE_DAYS).length;

  return (
    <>
      <QuickAdd shopId={shopId} families={families} products={products} onAdded={load} />
      <div className="card">
        <h2 className="card-title">{t("shop.catalog.title", { n: products.length })}</h2>
        {old > 0 && <p className="notice">{t("shop.price.reminder", { n: old })}</p>}
        <div className="row">
          <div>
            <label htmlFor="c-q">{t("shop.catalog.search")}</label>
            <input id="c-q" type="search" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <div>
            <label htmlFor="c-fam">{t("shop.catalog.family")}</label>
            <select id="c-fam" value={fam} onChange={(e) => setFam(e.target.value)}>
              <option value="">{t("shop.catalog.allFamilies")}</option>
              {families.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </div>
        </div>
        {products.length === 0 && <p className="help">{t("shop.catalog.empty")}</p>}
        <ul className="list product-list">
          {shown.map((p) => <ProductRow key={p.id} shopId={shopId} p={p} catName={catName(p.category_id)} onChange={load} />)}
        </ul>
      </div>
      <ImportBox shopId={shopId} onDone={load} />
    </>
  );
}
