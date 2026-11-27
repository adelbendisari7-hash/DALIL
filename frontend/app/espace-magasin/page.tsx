"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import ShopForm, { cleanShop, type ShopFormValue } from "@/components/ShopForm";
import ShopCatalog from "@/components/ShopCatalog";
import ShopWizard from "@/components/ShopWizard";
import { photoForm, shrinkPhoto } from "@/lib/photo";
import type { Opening } from "@/components/HoursPicker";
import { api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

type Shop = Omit<ShopFormValue, "opening"> & {
  id: number; status: string; verified: boolean; photo_url: string | null; verified_at: string | null; reject_reason: string | null;
  opening: Opening | null; closed_until: string | null; closed_note: string | null;
  open_status: { open: boolean; label: string } | null;
  brands: { brand_id: number; confirmed_at: string | null }[]; categories: { category_id: number; confirmed_at: string | null }[];
};
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
  const [count, setCount] = useState<number | null>(null);
  const [inbox, setInbox] = useState<Inbox[]>([]);
  const [msg, setMsg] = useState("");

  const reloadInbox = useCallback(() => {
    api<Inbox[]>("/part-requests/inbox").then((r) => setInbox(r.filter((x) => x.shop_id === shop.id))).catch(() => undefined);
  }, [shop.id]);
  useEffect(() => {
    reloadInbox();
    api<{ id: number }[]>(`/shops/${shop.id}/products`).then((p) => setCount(p.length)).catch(() => undefined);
  }, [reloadInbox, shop.id]);

  async function respond(requestId: number, available: boolean) {
    const price = available ? window.prompt(t("shop.product.price")) : null;
    await api(`/part-requests/${requestId}/responses?shop_id=${shop.id}`, {
      method: "POST", json: { available, price: price ? Number(price) || null : null },
    }).catch(() => undefined);
    reloadInbox();
  }

  async function saveProfile(v: ShopFormValue) {
    try {
      await api(`/shops/${shop.id}`, { method: "PATCH", json: cleanShop(v) });
      setMsg(t("shop.saved"));
      onChange();
    } catch (err) { setMsg(errMsg(err)); }
  }

  async function storefront(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    try {
      const b = await shrinkPhoto(f);
      await api(`/shops/${shop.id}/photo`, { method: "POST", body: photoForm(b) });
      onChange();
    } catch (err) { setMsg(err instanceof ApiError ? errMsg(err) : t("shop.photo.unreadable")); }
  }

  const waiting = inbox.filter((r) => r.available === null).length;
  return (
    <div>
      <ShopStatus shop={shop} onChange={onChange} />
      <div className="tabs" role="tablist">
        {(["inbox", "catalog", "profile"] as const).map((k) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}>
            {k === "inbox" ? `${t("shop.inbox")}${waiting ? ` (${waiting})` : ""}`
              : k === "catalog" ? `${t("shop.products")}${count != null ? ` (${count})` : ""}` : t("shop.profile")}
          </button>
        ))}
      </div>
      {msg && <p className="help" role="status">{msg}</p>}

      {tab === "inbox" && (inbox.length ? (
        <div className="card">
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
        </div>
      ) : <p className="help">{t("shop.inbox.empty")}</p>)}

      {tab === "catalog" && <ShopCatalog shopId={shop.id} onCount={setCount} />}

      {tab === "profile" && (
        <>
          <div className="card">
            <h2 className="card-title">{t("shop.storefront.title")}</h2>
            <p className="help" style={{ marginTop: 0 }}>{t("shop.storefront.help")}</p>
            <div className="photo-row">
              {shop.photo_url && <img src={shop.photo_url} alt={t("shop.storefront.title")} className="storefront" />}
              <label className="btn btn-ghost photo-button">
                {shop.photo_url ? t("shop.photo.change") : t("shop.storefront.add")}
                <input type="file" accept="image/*" capture="environment" onChange={storefront} hidden />
              </label>
            </div>
          </div>
          <div className="card">
            <ShopForm
              showPhone
              initial={{ ...shop, landmark: shop.landmark ?? "", brand_ids: shop.brands.map((b) => b.brand_id), category_ids: shop.categories.map((c) => c.category_id) }}
              submitLabel={t("shop.save")}
              onSubmit={saveProfile}
            />
          </div>
        </>
      )}
    </div>
  );
}
