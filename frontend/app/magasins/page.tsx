"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import ShopContact from "@/components/ShopContact";
import { api, requestStore, vehicleStore } from "@/lib/api";
import { t } from "@/lib/i18n";

const ShopMap = dynamic(() => import("@/components/ShopMap"), { ssr: false });

type Rec = {
  id: number; name: string; lat: number | null; lng: number | null; commune: string | null;
  phone: string | null; whatsapp: string | null; hours: string | null; is_demo: boolean;
  score: number; reasons: string[]; stale: boolean; distance_km: number | null;
  verified: boolean; landmark: string | null; open_status: { open: boolean; label: string } | null; fast_reply?: boolean;
  offer: Offer | null;
};
type Offer = { title: string; price: number; condition: string; oem_ref: string | null; compatible: boolean | null;
  count: number; confirmed_days: number | null };

function Shops() {
  const sp = useSearchParams();
  const categoryId = Number(sp.get("category"));
  const partName = sp.get("part") || "";
  const sessionId = sp.get("session") ? Number(sp.get("session")) : undefined;
  const variantParam = sp.get("variant");
  const [variantId, setVariantId] = useState<number | undefined>(variantParam ? Number(variantParam) : undefined);
  const [me, setMe] = useState<[number, number] | null>(null);
  const [geo, setGeo] = useState<"idle" | "busy" | "denied">("idle");
  const [shops, setShops] = useState<Rec[] | null>(null);
  const [view, setView] = useState<"list" | "map">("list");
  const [error, setError] = useState("");
  const [requestMsg, setRequestMsg] = useState("");
  const [requestSent, setRequestSent] = useState(false);
  const [sort, setSort] = useState<"score" | "price">("score");

  useEffect(() => {
    if (!variantParam) setVariantId(vehicleStore.get()?.variantId);
  }, [variantParam]);

  useEffect(() => {
    if (!categoryId) return;
    const q = new URLSearchParams({ category_id: String(categoryId) });
    if (variantId) q.set("variant_id", String(variantId));
    if (me) {
      q.set("lat", String(me[0]));
      q.set("lng", String(me[1]));
    }
    api<Rec[]>(`/shops/recommend?${q}`).then(setShops).catch(() => setError(t("common.error")));
  }, [categoryId, variantId, me]);

  function locate() {
    if (!navigator.geolocation) return setGeo("denied");
    setGeo("busy");
    navigator.geolocation.getCurrentPosition(
      (p) => { setMe([p.coords.latitude, p.coords.longitude]); setGeo("idle"); },
      () => setGeo("denied"),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  }

  async function broadcast() {
    try {
      const r = await api<{ id: number; token: string; notified_shops: number }>("/part-requests", {
        method: "POST", json: { category_id: categoryId, variant_id: variantId ?? null, session_id: sessionId ?? null },
      });
      requestStore.add({ id: r.id, token: r.token });   // suivi des réponses, même sans compte
      setRequestSent(r.notified_shops > 0);
      setRequestMsg(r.notified_shops ? t("shops.request.sent", { n: r.notified_shops }) : t("shops.request.none"));
    } catch {
      setRequestMsg(t("common.error"));
    }
  }

  const ctx = useMemo(() => ({ categoryId, variantId, sessionId, partName }), [categoryId, variantId, sessionId, partName]);
  if (!categoryId) return <p><Link href="/pieces">{t("parts.title")}</Link></p>;

  return (
    <section>
      <h1>{t("shops.title")} {partName.toLowerCase()}</h1>
      {vehicleStore.get() && variantId && <p className="meta">{t("result.for")} {vehicleStore.get()?.label}</p>}

      <div className="actions" style={{ alignItems: "center" }}>
        <div className="toggle" role="group">
          <button aria-pressed={view === "list"} onClick={() => setView("list")}>{t("shops.list")}</button>
          <button aria-pressed={view === "map"} onClick={() => setView("map")}>{t("shops.map")}</button>
        </div>
        {!me && (
          <button className="btn btn-ghost" onClick={locate} disabled={geo === "busy"}>
            {geo === "busy" ? t("shops.locating") : t("shops.locate")}
          </button>
        )}
      </div>
      <p className="help">{geo === "denied" ? t("shops.locate.denied") : t("shops.locate.help")}</p>

      {error && <p className="err" role="alert">{error}</p>}
      {!shops && !error && <p>{t("common.loading")}</p>}
      {shops && shops.length === 0 && <p>{t("shops.empty")}</p>}

      {shops && shops.length > 0 && view === "map" && <ShopMap shops={shops} me={me} />}
      {shops && shops.some((x) => x.offer) && view === "list" && (
        <div className="toggle sort-toggle" role="group" aria-label={t("shops.sort")}>
          <button aria-pressed={sort === "score"} onClick={() => setSort("score")}>{t("shops.sort.score")}</button>
          <button aria-pressed={sort === "price"} onClick={() => setSort("price")}>{t("shops.sort.price")}</button>
        </div>
      )}
      {shops && shops.length > 0 && view === "list" && (
        <ol className="shops">
          {(sort === "price"
            ? [...shops].sort((a, b) => (a.offer?.price ?? Infinity) - (b.offer?.price ?? Infinity))
            : shops).map((s) => (
            <li className="shop" key={s.id}>
              <h3>
                <Link href={`/magasins/${s.id}`}>{s.name}</Link>
                {s.is_demo && <span className="tag-demo" title={t("shops.demo")}>démo</span>}
              </h3>
              <div className="shop-badges">
                {s.verified && <span className="badge-verified">{t("shop.verified")}</span>}
                {s.fast_reply && <span className="badge-verified badge-fast">{t("stats.fast")}</span>}
                {s.open_status && <span className={`open-pill ${s.open_status.open ? "is-open" : ""}`}>{s.open_status.label}</span>}
              </div>
              <span className="meta">{[s.commune, s.landmark, s.open_status ? null : s.hours].filter(Boolean).join(" · ")}</span>
              {s.offer && (
                <div className="offer">
                  <strong className="offer-price">{s.offer.price.toLocaleString("fr-FR")} DA</strong>
                  <span className="meta">
                    {s.offer.title} · {t(`shop.condition.${s.offer.condition}`)}
                    {s.offer.compatible === true && <> · <span className="ok">{t("shops.offer.fits")}</span></>}
                    {s.offer.compatible === false && ` · ${t("shops.offer.check")}`}
                    {s.offer.count > 1 && ` · ${t("shops.offer.more", { n: s.offer.count - 1 })}`}
                  </span>
                  {s.offer.confirmed_days != null && s.offer.confirmed_days > 30 && (
                    <span className="meta">{t("shops.offer.age", { n: s.offer.confirmed_days })}</span>
                  )}
                </div>
              )}
              <ul className="reasons">
                {s.reasons.map((r) => <li key={r} className={r === "fiche à reconfirmer" ? "warn" : undefined}>{r}</li>)}
              </ul>
              <ShopContact shop={s} ctx={ctx} />
            </li>
          ))}
        </ol>
      )}

      <div className="section">
        <button className="btn btn-ghost" onClick={broadcast}>{t("shops.request")}</button>
        {requestMsg && <p className="help" role="status">{requestMsg}</p>}
        {requestSent && <Link className="btn" href="/demandes">{t("requests.follow")}</Link>}
      </div>
    </section>
  );
}

export default function ShopsPage() {
  return (
    <Suspense fallback={<p>{t("common.loading")}</p>}>
      <Shops />
    </Suspense>
  );
}
