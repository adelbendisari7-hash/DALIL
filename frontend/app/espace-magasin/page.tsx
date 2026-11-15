"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import ShopForm, { cleanShop, type ShopFormValue } from "@/components/ShopForm";
import { api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

type Shop = ShopFormValue & { id: number; status: string; brands: { brand_id: number }[]; categories: { category_id: number }[] };
type Product = { id: number; title: string; oem_ref: string | null; price: number | null; condition: string; category_id: number };
type Family = { id: number; name: string; children: { id: number; name: string }[] };
type Inbox = { request_id: number; shop_id: number; part: string; vehicle: string | null; available: boolean | null };
type Claimable = { id: number; name: string; commune: string | null };

const errMsg = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));

export default function ShopSpace() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [shops, setShops] = useState<Shop[]>([]);
  const [claimable, setClaimable] = useState<Claimable[]>([]);
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    const u = session.user();
    setUser(u);
    setReady(true);
    if (!u) return;
    setShops(await api<Shop[]>("/shops/mine").catch(() => []));
    setClaimable(await api<Claimable[]>(`/shops/claimable?phone=${encodeURIComponent(u.phone)}`).catch(() => []));
  }, []);

  useEffect(() => { load(); }, [load]);

  async function becomeOwner() {
    if (user && user.role !== "shop_owner" && user.role !== "admin") {
      const r = await api<{ token: string; user: User }>("/auth/me", { method: "PATCH", json: { role: "shop_owner" } });
      session.save(r.token, r.user);
    }
  }

  async function register(v: ShopFormValue) {
    try {
      await becomeOwner();
      await api("/shops", { method: "POST", json: cleanShop(v) });
      await load();
    } catch (e) { setMsg(errMsg(e)); }
  }

  async function claim(id: number) {
    try {
      await api(`/shops/${id}/claim`, { method: "POST" });
      await load();
    } catch (e) { setMsg(errMsg(e)); }
  }

  if (!ready) return <p>{t("common.loading")}</p>;
  if (!user) {
    return (
      <section>
        <h1>{t("shop.title")}</h1>
        <p>{t("shop.lead")}</p>
        <p>{t("shop.loginFirst")}</p>
        <Link className="btn" href="/connexion?next=/espace-magasin">{t("nav.login")}</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>{t("shop.title")}</h1>
      {msg && <p className="err" role="alert">{msg}</p>}
      {claimable.length > 0 && (
        <div className="questions">
          <h3>{t("shop.claim.title")}</h3>
          <ul className="list">
            {claimable.map((c) => (
              <li key={c.id}><span>{c.name} {c.commune ? `(${c.commune})` : ""}</span><button className="btn" onClick={() => claim(c.id)}>{t("shop.claim.button")}</button></li>
            ))}
          </ul>
        </div>
      )}
      {shops.length === 0 ? (
        <>
          <p>{t("shop.lead")}</p>
          <h2>{t("shop.register")}</h2>
          <ShopForm showPhone={false} submitLabel={t("shop.register")} onSubmit={register} />
        </>
      ) : (
        shops.map((s) => <ShopAdmin key={s.id} shop={s} onChange={load} />)
      )}
    </section>
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
    <div className="section">
      <h2>{shop.name}</h2>
      <p className={shop.status === "draft" ? "meta" : "ok"}>{t(`shop.status.${shop.status}`)}</p>
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
          initial={{ ...shop, brand_ids: shop.brands.map((b) => b.brand_id), category_ids: shop.categories.map((c) => c.category_id) }}
          submitLabel={t("shop.save")}
          onSubmit={saveProfile}
        />
      )}
    </div>
  );
}
