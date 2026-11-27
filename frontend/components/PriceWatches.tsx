"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export type Watch = {
  id: number; category_id: number; part: string | null; variant_id: number | null; reference_price: number | null;
  lowest: { price: number; shop: { id: number; name: string }; shops: number; demo: boolean } | null;
  alert: "drop" | "available" | null; drop_pct: number | null; since: string;
};

const da = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} DA`;

export function shopsLink(w: Pick<Watch, "category_id" | "part" | "variant_id">): string {
  const q = new URLSearchParams({ category: String(w.category_id), part: w.part ?? "" });
  if (w.variant_id) q.set("variant", String(w.variant_id));
  return `/magasins?${q}`;
}

/** Une ligne d'alerte : « Plaquettes : 4 000 DA (- 20 %) chez Magasin X » */
export function watchLine(w: Watch): string {
  if (!w.lowest) return t("watch.noPrice");
  if (w.alert === "drop") return t("watch.drop", { price: da(w.lowest.price), pct: w.drop_pct ?? 0, shop: w.lowest.shop.name });
  if (w.alert === "available") return t("watch.available", { price: da(w.lowest.price), shop: w.lowest.shop.name });
  return t("watch.now", { price: da(w.lowest.price), shop: w.lowest.shop.name });
}

/** « Prix suivis » dans Mon compte : prix le plus bas du moment, alerte, « Vu », « Ne plus suivre ». */
export default function PriceWatches() {
  const [list, setList] = useState<Watch[] | null>(null);
  const load = useCallback(() => { api<Watch[]>("/me/price-watches").then(setList).catch(() => setList([])); }, []);
  useEffect(() => { load(); }, [load]);

  async function act(w: Watch, what: "seen" | "delete") {
    await api(`/me/price-watches/${w.id}${what === "seen" ? "/seen" : ""}`, { method: what === "seen" ? "POST" : "DELETE" })
      .catch(() => undefined);
    load();
    window.dispatchEvent(new Event("dalil-alerts"));
  }

  if (!list) return null;
  return (
    <section className="card" aria-labelledby="watches-title">
      <h2 id="watches-title" className="card-title">{t("watch.title")}</h2>
      {list.length === 0 ? <p className="help" style={{ marginTop: 0 }}>{t("watch.empty")}</p> : (
        <ul className="carnet-list">
          {list.map((w) => (
            <li key={w.id} className={`visit watch${w.alert ? " has-alert" : ""}`}>
              <div className="status-head">
                <strong><Link href={shopsLink(w)}>{w.part}</Link></strong>
                {w.alert && <span className="maint-pill paper-pill is-ok">{t(`watch.badge.${w.alert}`)}</span>}
              </div>
              <span className="meta">
                {watchLine(w)}{w.lowest?.demo ? ` · ${t("watch.demo")}` : ""}
              </span>
              {w.reference_price != null && <span className="meta">{t("watch.reference", { price: da(w.reference_price) })}</span>}
              <div className="actions" style={{ marginTop: "0.3rem" }}>
                {w.alert && <button type="button" className="chip" onClick={() => act(w, "seen")}>{t("watch.seen")}</button>}
                <button type="button" className="chip" onClick={() => act(w, "delete")}
                  aria-label={t("watch.stopFor", { part: w.part ?? "" })}>{t("watch.stop")}</button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <p className="help">{t("watch.help")}</p>
    </section>
  );
}
