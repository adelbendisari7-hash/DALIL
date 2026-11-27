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
  landmark: string | null; verified: boolean; open_status: { open: boolean; label: string } | null;
};
type Product = { id: number; title: string; oem_ref: string | null; price: number | null; condition: string; in_stock: boolean };
type Named = { id: number; name: string };
type Family = Named & { children: Named[] };

export default function ShopPage() {
  const { id } = useParams<{ id: string }>();
  const [shop, setShop] = useState<Shop | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [brands, setBrands] = useState<Named[]>([]);
  const [cats, setCats] = useState<Named[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Shop>(`/shops/${id}`).then(setShop)
      .catch((e) => setError(e instanceof ApiError && e.status === 404 ? t("shop.notFound") : t("common.error")));
    api<Product[]>(`/shops/${id}/products`).then(setProducts).catch(() => undefined);
    api<Named[]>("/vehicles/brands").then(setBrands).catch(() => undefined);
    api<Family[]>("/parts/categories").then((f) => setCats(f.flatMap((x) => [x, ...x.children]))).catch(() => undefined);
  }, [id]);

  if (error) return <p className="err">{error}</p>;
  if (!shop) return <p>{t("common.loading")}</p>;
  const name = (list: Named[], i: number) => list.find((x) => x.id === i)?.name;

  return (
    <article>
      <h1>
        {shop.name}
        {shop.is_demo && <span className="tag-demo">démo</span>}
      </h1>
      {shop.verified && <p className="badge-verified">{t("shop.verified")}</p>}
      {shop.is_demo && <p className="notice">{t("shops.demo")}</p>}
      <p className="meta">{[shop.address, shop.commune].filter(Boolean).join(", ")}</p>
      {shop.landmark && <p className="meta">{t("shop.landmark")} : {shop.landmark}</p>}
      {shop.open_status && <p className={`open-pill ${shop.open_status.open ? "is-open" : ""}`}>{shop.open_status.label}</p>}
      {shop.hours && <p>{t("shops.hours")} : {shop.hours}</p>}
      <ShopContact shop={shop} ctx={{}} />

      <h3 className="section">{t("shop.brands")}</h3>
      <div className="chips">{shop.brands.map((b) => <span key={b.brand_id} className="chip">{name(brands, b.brand_id)}</span>)}</div>
      <h3 className="section">{t("shop.categories")}</h3>
      <div className="chips">{shop.categories.map((c) => <span key={c.category_id} className="chip">{name(cats, c.category_id)}</span>)}</div>

      {products.length > 0 && (
        <>
          <h3 className="section">{t("shop.products")}</h3>
          <ul className="list">
            {products.map((p) => (
              <li key={p.id}>
                <span>{p.title}{p.oem_ref ? ` (réf. ${p.oem_ref})` : ""}</span>
                <span className="meta">{p.price ? `${p.price.toLocaleString("fr-DZ")} DA` : ""} {t(`shop.condition.${p.condition}`)}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      {shop.lat != null && <ShopMap shops={[shop]} />}
    </article>
  );
}
