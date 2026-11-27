"use client";
import qrcode from "qrcode-generator";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Shop = { id: number; name: string; address: string | null; landmark: string | null; commune: string | null;
  hours: string | null; verified: boolean };

/** QR code en SVG (bibliothèque qrcode-generator, licence MIT), correction d'erreur moyenne : lisible même un peu
 * abîmé ou mal éclairé au comptoir. */
function Qr({ text }: { text: string }) {
  const svg = useMemo(() => {
    const q = qrcode(0, "M");
    q.addData(text);
    q.make();
    return q.createSvgTag({ cellSize: 8, margin: 2, scalable: true });
  }, [text]);
  return <div className="poster-qr" role="img" aria-label={t("shop.poster.qr")} dangerouslySetInnerHTML={{ __html: svg }} />;
}

/** Idée A du plan côté magasin : affiche « Trouvez-nous sur DALIL » à imprimer pour le comptoir. */
function Poster() {
  const id = useSearchParams().get("magasin");
  const [shop, setShop] = useState<Shop | null>(null);
  const [origin, setOrigin] = useState("");
  useEffect(() => {
    // Adresse publique du site si elle est connue (mise en ligne), sinon celle d'où la page est ouverte
    setOrigin(process.env.NEXT_PUBLIC_SITE_URL || window.location.origin);
    if (id) api<Shop>(`/shops/${id}`).then(setShop).catch(() => setShop(null));
  }, [id]);

  if (!shop) return <p>{t("common.loading")}</p>;
  const url = `${origin}/magasins/${shop.id}`;
  const provisional = /localhost|127\.0\.0\.1|^http:\/\/(192\.168|10\.|172\.)/.test(origin);
  return (
    <section>
      <div className="no-print">
        <h1>{t("shop.poster.title")}</h1>
        <p className="help">{t("shop.poster.help")}</p>
        {provisional && <p className="notice">{t("shop.poster.provisional")}</p>}
        <div className="actions"><button className="btn btn-primary" onClick={() => window.print()}>{t("shop.poster.print")}</button></div>
      </div>
      <article className="poster">
        <p className="poster-brand">● DALIL</p>
        <h2 className="poster-title">{t("shop.poster.headline")}</h2>
        <p className="poster-shop">{shop.name}</p>
        {shop.verified && <p className="badge-verified">{t("shop.verified")}</p>}
        <Qr text={url} />
        <p className="poster-scan">{t("shop.poster.scan")}</p>
        <p className="poster-meta">{[shop.address, shop.landmark, shop.commune].filter(Boolean).join(" · ")}</p>
        {shop.hours && <p className="poster-meta">{shop.hours}</p>}
        <p className="poster-url">{url.replace(/^https?:\/\//, "")}</p>
      </article>
    </section>
  );
}

export default function PosterPage() {
  return (
    <Suspense fallback={null}>
      <Poster />
    </Suspense>
  );
}
