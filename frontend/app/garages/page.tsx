"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import ShopContact from "@/components/ShopContact";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Garage = {
  id: number; name: string; commune: string | null; phone: string | null; whatsapp: string | null; is_demo: boolean;
  verified: boolean; landmark: string | null; hours: string | null; open_status: { open: boolean; label: string } | null;
  specialties: string[]; reasons: string[]; distance_km: number | null; match: number;
};

/** Mécaniciens pour la pièce trouvée par le diagnostic : spécialité, proximité, ouvert maintenant. */
function Garages() {
  const sp = useSearchParams();
  const categoryId = sp.get("category");
  const part = sp.get("part") || "";
  const [me, setMe] = useState<[number, number] | null>(null);
  const [geo, setGeo] = useState<"idle" | "busy" | "denied">("idle");
  const [list, setList] = useState<Garage[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const q = new URLSearchParams();
    if (categoryId) q.set("category_id", categoryId);
    if (me) { q.set("lat", String(me[0])); q.set("lng", String(me[1])); }
    api<Garage[]>(`/garages/recommend?${q}`).then(setList).catch(() => setError(t("common.error")));
  }, [categoryId, me]);

  function locate() {
    if (!navigator.geolocation) return setGeo("denied");
    setGeo("busy");
    navigator.geolocation.getCurrentPosition(
      (p) => { setMe([p.coords.latitude, p.coords.longitude]); setGeo("idle"); },
      () => setGeo("denied"),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }

  return (
    <section>
      <h1>{part ? t("garages.titleFor", { part: part.toLowerCase() }) : t("garages.title")}</h1>
      <p className="lead">{t("garages.lead")}</p>
      {!me && (
        <div className="actions">
          <button className="btn btn-ghost" onClick={locate} disabled={geo === "busy"}>{geo === "busy" ? t("shops.locating") : t("shops.locate")}</button>
        </div>
      )}
      {geo === "denied" && <p className="help">{t("shops.locate.denied")}</p>}
      {error && <p className="err" role="alert">{error}</p>}
      {!list && !error && <p>{t("common.loading")}</p>}
      {list && list.length === 0 && (
        <div className="card">
          <p style={{ marginTop: 0 }}>{t("garages.empty")}</p>
          {categoryId && <Link className="btn btn-ghost" href={`/magasins?category=${categoryId}&part=${encodeURIComponent(part)}`}>{t("garages.backToShops")}</Link>}
        </div>
      )}
      {list && list.length > 0 && (
        <ol className="shops">
          {list.map((g) => (
            <li className="shop garage" key={g.id}>
              <h3>
                <Link href={`/magasins/${g.id}`}>{g.name}</Link>
                {g.is_demo && <span className="tag-demo">démo</span>}
              </h3>
              <div className="shop-badges">
                {g.verified && <span className="badge-verified">{t("shop.verified")}</span>}
                {g.open_status && <span className={`open-pill ${g.open_status.open ? "is-open" : ""}`}>{g.open_status.label}</span>}
              </div>
              <span className="meta">{[g.commune, g.landmark, g.open_status ? null : g.hours].filter(Boolean).join(" · ")}</span>
              {g.specialties.length > 0 && (
                <div className="chips">{g.specialties.map((s) => <span key={s} className="chip chip-static">{s}</span>)}</div>
              )}
              <ul className="reasons">{g.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
              <ShopContact shop={{ ...g, shop_type: "garage" }} ctx={{ partName: part }} />
            </li>
          ))}
        </ol>
      )}
      <p className="help">{t("garages.note")}</p>
    </section>
  );
}

export default function GaragesPage() {
  return (
    <Suspense fallback={<p>{t("common.loading")}</p>}>
      <Garages />
    </Suspense>
  );
}
