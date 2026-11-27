"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import ShopForm, { cleanShop, type ShopFormValue } from "@/components/ShopForm";
import ShopWizard from "@/components/ShopWizard";
import type { Opening } from "@/components/HoursPicker";
import { API, api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

type Shop = Omit<ShopFormValue, "opening"> & {
  id: number; status: string; verified: boolean; verified_at: string | null; reject_reason: string | null;
  opening: Opening | null; closed_until: string | null; closed_note: string | null;
  open_status: { open: boolean; label: string } | null;
  brands: { brand_id: number; confirmed_at: string | null }[]; categories: { category_id: number; confirmed_at: string | null }[];
};
type Product = { id: number; title: string; oem_ref: string | null; price: number | null; condition: string; category_id: number };
type Family = { id: number; name: string; children: { id: number; name: string }[] };
type Inbox = { request_id: number; shop_id: number; part: string; vehicle: string | null; available: boolean | null };
type Claim = { id: number; status: string; reason: string | null; shop: { id: number; name: string; commune: string | null } | null };

const errMsg = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));
const RECONFIRM_DAYS = 150;   // un mois avant les six mois de la règle de fraîcheur

export default function ShopSpace() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [shops, setShops] = useState<Shop[] | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [note, setNote] = useState("");

  const load = useCallback(async () => {
    const u = session.user();
    setUser(u);
    setReady(true);
    if (!u) return;
    setShops(await api<Shop[]>("/shops/mine").catch(() => []));
    setClaims(await api<Claim[]>("/shops/claims/mine").catch(() => []));
  }, []);

  useEffect(() => { load(); }, [load]);

  async function becomeOwner() {
    const u = session.user();
    if (u && u.role !== "shop_owner" && u.role !== "admin") {
      const r = await api<{ token: string; user: User }>("/auth/me", { method: "PATCH", json: { role: "shop_owner" } });
      session.save(r.token, r.user);
    }
  }

  if (!ready) return <p>{t("common.loading")}</p>;
  if (!user) {
    return (
      <section>
        <h1>{t("shop.title")}</h1>
        <p className="lead">{t("shop.lead")}</p>
        <div className="card">
          <p>{t("shop.loginFirst")}</p>
          <div className="actions">
            <Link className="btn btn-primary" href="/connexion?inscription=1&next=/espace-magasin">{t("login.tab.register")}</Link>
            <Link className="btn btn-ghost" href="/connexion?next=/espace-magasin">{t("nav.login")}</Link>
          </div>
        </div>
      </section>
    );
  }
  if (shops === null) return <p>{t("common.loading")}</p>;

  const pending = claims.filter((c) => c.status === "pending");
  return (
    <section>
      <h1>{t("shop.title")}</h1>
      {note && <p className="notice" role="status">{note}</p>}
      {claims.filter((c) => c.status !== "accepted").map((c) => (
        <div key={c.id} className={`card status-card ${c.status === "rejected" ? "is-rejected" : "is-pending"}`}>
          <strong>{c.shop?.name}</strong>
          <p className="help" style={{ marginTop: "0.25rem" }}>
            {c.status === "pending" ? t("shop.claim.pending") : `${t("shop.claim.rejected")}${c.reason ? ` : ${c.reason}` : ""}`}
          </p>
        </div>
      ))}
      {shops.length === 0 ? (
        pending.length === 0 && (
          <>
            <p className="lead">{t("shop.lead")}</p>
            <ShopWizard defaultPhone={user.phone} becomeOwner={becomeOwner}
              onDone={(msg) => { setNote(msg ?? ""); load(); }} />
          </>
        )
      ) : (
        shops.map((s) => <ShopAdmin key={s.id} shop={s} onChange={load} />)
      )}
    </section>
  );
}

/** En-tête de la gestion du magasin : statut (vérification, refus et motif, badge), fermeture exceptionnelle,
 * reconfirmation des informations, affiche à imprimer. */
function ShopStatus({ shop, onChange }: { shop: Shop; onChange: () => void }) {
  const [closing, setClosing] = useState(false);
  const [until, setUntil] = useState("");
  const [why, setWhy] = useState("");
  const [msg, setMsg] = useState("");
  const oldest = Math.min(...[...shop.brands, ...shop.categories].map((l) => (l.confirmed_at ? Date.parse(l.confirmed_at) : Date.now())));
  const stale = Number.isFinite(oldest) && Date.now() - oldest > RECONFIRM_DAYS * 86_400_000;

  async function patch(json: Record<string, unknown>) {
    try {
      await api(`/shops/${shop.id}`, { method: "PATCH", json });
      setClosing(false);
      onChange();
    } catch (e) { setMsg(errMsg(e)); }
  }

  return (
    <div className={`card status-card is-${shop.status}`}>
      <div className="status-head">
        <h2 className="card-title" style={{ margin: 0 }}>{shop.name}</h2>
        {shop.verified && <span className="badge-verified">{t("shop.verified")}</span>}
      </div>
      <p className="help">
        {shop.status === "draft" && t("shop.status.draft")}
        {shop.status === "rejected" && `${t("shop.status.rejected")}${shop.reject_reason ? ` ${t("shop.status.reason")} : ${shop.reject_reason}` : ""}`}
        {shop.verified && shop.verified_at && t("shop.verifiedOn", { date: new Date(shop.verified_at).toLocaleDateString("fr-FR") })}
      </p>
      {shop.open_status && <p className={`open-pill ${shop.open_status.open ? "is-open" : ""}`}>{shop.open_status.label}</p>}
      {stale && (
        <div className="notice">
          {t("shop.reconfirm.text")}{" "}
          <button type="button" className="btn btn-ghost" onClick={async () => { await api(`/shops/${shop.id}/reconfirm`, { method: "POST" }).catch(() => undefined); onChange(); }}>
            {t("shop.reconfirm.button")}
          </button>
        </div>
      )}
      <div className="actions">
        {shop.closed_until ? (
          <button type="button" className="btn btn-ghost" onClick={() => patch({ closed_until: null })}>{t("shop.closed.reopen")}</button>
        ) : (
          <button type="button" className="btn btn-ghost" onClick={() => setClosing(!closing)}>{t("shop.closed.button")}</button>
        )}
        {shop.verified && <Link className="btn btn-ghost" href={`/espace-magasin/affiche?magasin=${shop.id}`}>{t("shop.poster.button")}</Link>}
      </div>
      {closing && (
        <div className="car-form">
          <div className="row">
            <div>
              <label htmlFor="cl-until">{t("shop.closed.until")}</label>
              <input id="cl-until" type="date" value={until} onChange={(e) => setUntil(e.target.value)} />
            </div>
            <div>
              <label htmlFor="cl-why">{t("shop.closed.why")}</label>
              <input id="cl-why" maxLength={120} placeholder={t("shop.closed.why.placeholder")} value={why} onChange={(e) => setWhy(e.target.value)} />
            </div>
          </div>
          <div className="actions">
            <button type="button" className="btn" disabled={!until} onClick={() => patch({ closed_until: until, closed_note: why || null })}>{t("shop.closed.save")}</button>
          </div>
        </div>
      )}
      {msg && <p className="err" role="alert">{msg}</p>}
    </div>
  );
}

function ShopAdmin({ shop, onChange }: { shop: Shop; onChange: () => void }) {
  const [tab, setTab] = useState<"inbox" | "catalog" | "profile">("inbox");
  const [products, setProducts] = useState<Product[]>([]);
  const [families, setFamilies] = useState<Family[]>([]);
  const [inbox, setInbox] = useState<Inbox[]>([]);
  const [msg, setMsg] = useState("");
  const [form, setForm] = useState({ title: "", category_id: "", oem_ref: "", price: "", condition: "adaptable", fits: "" });
  const [importMsg, setImportMsg] = useState("");

  const reload = useCallback(() => {
    api<Product[]>(`/shops/${shop.id}/products`).then(setProducts).catch(() => undefined);
    api<Inbox[]>("/part-requests/inbox").then((r) => setInbox(r.filter((x) => x.shop_id === shop.id))).catch(() => undefined);
  }, [shop.id]);

  useEffect(() => {
    reload();
    api<Family[]>("/parts/categories").then(setFamilies).catch(() => undefined);
  }, [reload]);

  async function addProduct(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      const variant_ids: number[] = [];
      if (form.fits.trim()) {
        // La compatibilité saisie en texte passe par l'import pour être résolue côté serveur.
        const csv = `titre;famille;reference;etat;prix;compatibilite\n${[form.title, families.flatMap((f) => f.children).find((c) => c.id === +form.category_id)?.name ?? "", form.oem_ref, form.condition, form.price, form.fits].map((x) => x.replaceAll(";", ",")).join(";")}`;
        const fd = new FormData();
        fd.append("file", new Blob([csv], { type: "text/csv" }), "produit.csv");
        const r = await api<{ errors: { error: string }[] }>(`/shops/${shop.id}/products/import`, { method: "POST", body: fd });
        if (r.errors.length) throw new ApiError(422, r.errors[0].error);
      } else {
        await api(`/shops/${shop.id}/products`, {
          method: "POST",
          json: { title: form.title, category_id: +form.category_id, oem_ref: form.oem_ref || null, price: form.price ? +form.price : null, condition: form.condition, variant_ids },
        });
      }
      setForm({ ...form, title: "", oem_ref: "", price: "" });
      setMsg(t("shop.product.added"));
      reload();
    } catch (err) { setMsg(errMsg(err)); }
  }

  async function importFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    try {
      const r = await api<{ created: number; updated: number; errors: { line: number; error: string }[] }>(`/shops/${shop.id}/products/import`, { method: "POST", body: fd });
      setImportMsg(t("shop.import.result", { created: r.created, updated: r.updated, errors: r.errors.length }) +
        (r.errors.length ? ` ${r.errors.slice(0, 3).map((x) => `ligne ${x.line} : ${x.error}`).join(" ; ")}` : ""));
      reload();
    } catch (err) { setImportMsg(errMsg(err)); }
    e.target.value = "";
  }

  async function respond(requestId: number, available: boolean) {
    const price = available ? window.prompt(t("shop.product.price")) : null;
    await api(`/part-requests/${requestId}/responses?shop_id=${shop.id}`, {
      method: "POST", json: { available, price: price ? Number(price) || null : null },
    }).catch(() => undefined);
    reload();
  }

  async function saveProfile(v: ShopFormValue) {
    try {
      await api(`/shops/${shop.id}`, { method: "PATCH", json: cleanShop(v) });
      setMsg(t("shop.saved"));
      onChange();
    } catch (err) { setMsg(errMsg(err)); }
  }

  const catName = (id: number) => families.flatMap((f) => f.children).find((c) => c.id === id)?.name ?? "";

  return (
    <div>
      <ShopStatus shop={shop} onChange={onChange} />
      <div className="tabs" role="tablist">
        {(["inbox", "catalog", "profile"] as const).map((k) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}>
            {k === "inbox" ? t("shop.inbox") : k === "catalog" ? `${t("shop.products")} (${products.length})` : t("shop.profile")}
          </button>
        ))}
      </div>
      {msg && <p className="help" role="status">{msg}</p>}

      {tab === "inbox" && (inbox.length ? (
        <ul className="list">
          {inbox.map((r) => (
            <li key={r.request_id}>
              <span><strong>{r.part}</strong>{r.vehicle ? `, ${r.vehicle}` : ""}</span>
              {r.available === null ? (
                <span className="actions" style={{ marginTop: 0 }}>
                  <button className="btn" onClick={() => respond(r.request_id, true)}>{t("shop.inbox.available")}</button>
                  <button className="btn btn-ghost" onClick={() => respond(r.request_id, false)}>{t("shop.inbox.unavailable")}</button>
                </span>
              ) : <span className="meta">{t("shop.inbox.answered")}</span>}
            </li>
          ))}
        </ul>
      ) : <p>{t("shop.inbox.empty")}</p>)}

      {tab === "catalog" && (
        <>
          <form onSubmit={addProduct}>
            <label htmlFor="p-title">{t("shop.product.title")}</label>
            <input id="p-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required minLength={2} />
            <div className="row">
              <div>
                <label htmlFor="p-cat">{t("shop.product.category")}</label>
                <select id="p-cat" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
                  <option value="">{t("vehicle.choose")}</option>
                  {families.map((f) => (
                    <optgroup key={f.id} label={f.name}>
                      {f.children.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </optgroup>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="p-price">{t("shop.product.price")}</label>
                <input id="p-price" inputMode="numeric" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value.replace(/[^\d]/g, "") })} />
              </div>
              <div>
                <label htmlFor="p-ref">{t("shop.product.ref")}</label>
                <input id="p-ref" value={form.oem_ref} onChange={(e) => setForm({ ...form, oem_ref: e.target.value })} />
              </div>
              <div>
                <label htmlFor="p-cond">{t("shop.product.condition")}</label>
                <select id="p-cond" value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })}>
                  {["neuf", "origine", "adaptable", "occasion"].map((c) => <option key={c} value={c}>{t(`shop.condition.${c}`)}</option>)}
                </select>
              </div>
            </div>
            <label htmlFor="p-fits">{t("shop.product.fits")}</label>
            <input id="p-fits" placeholder="Dacia Logan 1.5 dCi 2015; Renault Symbol 2016" value={form.fits} onChange={(e) => setForm({ ...form, fits: e.target.value })} />
            <div className="actions"><button className="btn">{t("shop.product.add")}</button></div>
          </form>

          <h3 className="section">{t("shop.import.title")}</h3>
          <p className="help">{t("shop.import.help")}</p>
          <p><a className="btn btn-ghost" href={`${API}/catalog/template.xlsx`} download>{t("shop.import.template")}</a></p>
          <input type="file" accept=".xlsx,.csv" onChange={importFile} aria-label={t("shop.import.title")} />
          {importMsg && <p className="help" role="status">{importMsg}</p>}

          <ul className="list section">
            {products.map((p) => (
              <li key={p.id}>
                <span>{p.title} <span className="meta">{catName(p.category_id)}{p.oem_ref ? `, réf. ${p.oem_ref}` : ""}</span></span>
                <span>
                  {p.price ? `${p.price.toLocaleString("fr-DZ")} DA ` : ""}
                  <button className="chip" onClick={async () => { await api(`/shops/${shop.id}/products/${p.id}`, { method: "DELETE" }); reload(); }}>{t("shop.product.delete")}</button>
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      {tab === "profile" && (
        <ShopForm
          showPhone
          initial={{ ...shop, landmark: shop.landmark ?? "", brand_ids: shop.brands.map((b) => b.brand_id), category_ids: shop.categories.map((c) => c.category_id) }}
          submitLabel={t("shop.save")}
          onSubmit={saveProfile}
        />
      )}
    </div>
  );
}
