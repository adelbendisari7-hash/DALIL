"use client";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ShopContact from "@/components/ShopContact";
import { api, ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";

const ShopMap = dynamic(() => import("@/components/ShopMap"), { ssr: false });

type Shop = {
  id: number; name: string; lat: number | null; lng: number | null; address: string | null; commune: string | null;
  phone: string | null; whatsapp: string | null; hours: string | null; is_demo: boolean; parts_origin: string[];
  brands: { brand_id: number }[]; categories: { category_id: number }[];
  landmark: string | null; verified: boolean; open_status: { open: boolean; label: string } | null; photo_url: string | null; fast_reply?: boolean;
  reviews?: Reviews;
  shop_type?: string; specialties?: string[];
};
type Reviews = { found: number; not_found: number; since: string | null;
  recent: { part: string | null; vehicle: string | null; date: string }[] };

// Jours du calendrier entre la date de l'avis (AAAA-MM-JJ) et aujourd'hui, sans effet d'heure ni de fuseau
const ago = (day: string) => {
  const [y, m, d] = day.split("-").map(Number);
  const now = new Date();
  const days = Math.round((Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) - Date.UTC(y, m - 1, d)) / 86_400_000);
  return days <= 0 ? t("reviews.today") : days === 1 ? t("reviews.yesterday") : t("reviews.daysAgo", { n: days });
};

/** Avis vérifiés : « pièce trouvée » de clients qui ont d'abord contacté le magasin depuis DALIL. Ni nom ni
 * commentaire : la pièce, la voiture et la date. */
function ShopReviews({ r }: { r: Reviews }) {
  const total = r.found + r.not_found;
  return (
    <section className="card reviews" aria-labelledby="rv-title">
      <h2 id="rv-title" className="card-title">{t("reviews.title")}</h2>
      {total === 0 ? (
        <p className="help" style={{ marginTop: 0 }}>{t("reviews.none")}</p>
      ) : (
        <>
          <p className="reviews-score">
            <strong>{r.found}</strong> {t(r.found === 1 ? "reviews.found1" : "reviews.foundN")}
            {r.not_found > 0 && <span className="meta"> · {t(r.not_found === 1 ? "reviews.notFound1" : "reviews.notFoundN", { n: r.not_found })}</span>}
          </p>
          {r.recent.length > 0 && (
            <ul className="list reviews-list">
              {r.recent.map((x, i) => (
                <li key={i}>
                  <span>{x.part ?? t("reviews.part")}{x.vehicle ? ` · ${x.vehicle}` : ""}</span>
                  <span className="meta">{ago(x.date)}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
      <p className="help">{t("reviews.how")}</p>
    </section>
  );
}
type Product = { id: number; title: string; oem_ref: string | null; price: number | null; condition: string; in_stock: boolean;
  photo_url: string | null };
type Named = { id: number; name: string };
type Family = Named & { children: Named[] };

export default function ShopPage() {
  const { id } = useParams<{ id: string }>();
  const [shop, setShop] = useState<Shop | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [brands, setBrands] = useState<Named[]>([]);
  const [cats, setCats] = useState<Named[]>([]);
  const [specialties, setSpecialties] = useState<{ slug: string; name: string }[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Shop>(`/shops/${id}`).then(setShop)
      .catch((e) => setError(e instanceof ApiError && e.status === 404 ? t("shop.notFound") : t("common.error")));
    api<Product[]>(`/shops/${id}/products`).then(setProducts).catch(() => undefined);
    api<Named[]>("/vehicles/brands").then(setBrands).catch(() => undefined);
    api<{ slug: string; name: string }[]>("/garages/specialties").then(setSpecialties).catch(() => undefined);
    api<Family[]>("/parts/categories").then((f) => setCats(f.flatMap((x) => [x, ...x.children]))).catch(() => undefined);
  }, [id]);

  if (error) return <p className="err">{error}</p>;
  if (!shop) return <p>{t("common.loading")}</p>;
  const name = (list: Named[], i: number) => list.find((x) => x.id === i)?.name;
  const specialtyName = Object.fromEntries(specialties.map((s) => [s.slug, s.name]));

  return (
    <article>
      <h1>
        {shop.name}
        {shop.is_demo && <span className="tag-demo">démo</span>}
      </h1>
      {shop.photo_url && <img src={shop.photo_url} alt={t("shop.storefront.title")} className="storefront storefront-hero" />}
      <div className="shop-badges">
        {shop.verified && <span className="badge-verified">{t("shop.verified")}</span>}
        {shop.fast_reply && <span className="badge-verified badge-fast">{t("stats.fast")}</span>}
      </div>
      {shop.is_demo && <p className="notice">{t("shops.demo")}</p>}
      <p className="meta">{[shop.address, shop.commune].filter(Boolean).join(", ")}</p>
      {shop.landmark && <p className="meta">{t("shop.landmark")} : {shop.landmark}</p>}
      {shop.open_status && <p className={`open-pill ${shop.open_status.open ? "is-open" : ""}`}>{shop.open_status.label}</p>}
      {shop.hours && <p>{t("shops.hours")} : {shop.hours}</p>}
      <ShopContact shop={shop} ctx={{}} />
      {shop.reviews && <ShopReviews r={shop.reviews} />}

      {shop.shop_type === "garage" && (shop.specialties?.length ?? 0) > 0 && (
        <>
          <h3 className="section">{t("garage.specialties.public")}</h3>
          <div className="chips">{shop.specialties!.map((s) => <span key={s} className="chip chip-static">{specialtyName[s] ?? s}</span>)}</div>
        </>
      )}
      <h3 className="section">{t(shop.shop_type === "garage" ? "garage.brands.public" : "shop.brands")}</h3>
      <div className="chips">{shop.brands.map((b) => <span key={b.brand_id} className="chip">{name(brands, b.brand_id)}</span>)}</div>
      <h3 className="section">{t("shop.categories")}</h3>
      <div className="chips">{shop.categories.map((c) => <span key={c.category_id} className="chip">{name(cats, c.category_id)}</span>)}</div>

      {products.length > 0 && (
        <>
          <h3 className="section">{t("shop.products")}</h3>
          <ul className="list">
            {products.map((p) => (
              <li key={p.id} className={`product-row${p.in_stock ? "" : " is-out"}`}>
                {p.photo_url ? <img src={p.photo_url} alt="" className="thumb" loading="lazy" /> : <span className="thumb thumb-empty" aria-hidden />}
                <span className="product-main">
                  <span>{p.title}{p.oem_ref ? ` (réf. ${p.oem_ref})` : ""}</span>
                  <span className="meta">{t(`shop.condition.${p.condition}`)}{p.in_stock ? "" : ` · ${t("shop.stock.out")}`}</span>
                </span>
                <strong className="product-side">{p.price ? `${p.price.toLocaleString("fr-FR")} DA` : ""}</strong>
              </li>
            ))}
          </ul>
        </>
      )}
      {shop.lat != null && <ShopMap shops={[shop]} />}
    </article>
  );
}
