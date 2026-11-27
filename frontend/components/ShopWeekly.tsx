"use client";
import { useEffect, useState } from "react";
import { api, store } from "@/lib/api";
import { t } from "@/lib/i18n";

type Period = { impressions: number; views: number; calls: number; whatsapp: number; requests: number; answered: number };
type Missing = { category_id: number; name: string; searches: number; sold: boolean; in_catalog: boolean };
type Weekly = { week: string; current: Period; previous: Period; missing: Missing[]; pending_requests: number;
  stale_prices: number; products: number; fast_reply: boolean };
export type ShopTab = "inbox" | "catalog" | "stats" | "profile" | "team";

function delta(cur: number, prev: number): string {
  if (cur === prev) return "=";
  return cur > prev ? `+${cur - prev}` : `${cur - prev}`;
}

/** « Votre semaine » en tête de l'espace magasin : chiffres des 7 derniers jours et ce qu'il y a à faire (pièces
 * cherchées près du magasin qu'il ne propose pas, demandes sans réponse, prix à confirmer). Repliable pour la semaine. */
export default function ShopWeekly({ shopId, go }: { shopId: number; go: (tab: ShopTab) => void }) {
  const [w, setW] = useState<Weekly | null>(null);
  const [hidden, setHidden] = useState(true);
  useEffect(() => {
    api<Weekly>(`/shops/${shopId}/weekly`).then((r) => {
      setW(r);
      setHidden(store.read(`dalil.weekly.${shopId}`) === r.week);
    }).catch(() => undefined);
  }, [shopId]);

  if (!w) return null;
  if (hidden) {
    return <button type="button" className="btn btn-ghost weekly-open" onClick={() => setHidden(false)}>{t("weekly.open")}</button>;
  }
  const c = w.current, p = w.previous;
  const todo: { text: string; action: string; tab: ShopTab }[] = [];
  for (const m of w.missing) {
    todo.push(m.sold
      ? { text: t("weekly.notInCatalog", { n: m.searches, part: m.name.toLowerCase() }), action: t("weekly.addProduct"), tab: "catalog" }
      : { text: t("weekly.notSold", { n: m.searches, part: m.name.toLowerCase() }), action: t("weekly.addFamily"), tab: "profile" });
  }
  if (w.pending_requests) todo.push({ text: t("weekly.pending", { n: w.pending_requests }), action: t("weekly.answer"), tab: "inbox" });
  if (w.stale_prices) todo.push({ text: t("weekly.stale", { n: w.stale_prices }), action: t("weekly.confirm"), tab: "catalog" });

  return (
    <section className="card weekly" aria-labelledby="weekly-title">
      <div className="upkeep-head">
        <h2 id="weekly-title" className="card-title">{t("weekly.title")}</h2>
        <button type="button" className="btn btn-ghost" onClick={() => { store.write(`dalil.weekly.${shopId}`, w.week); setHidden(true); }}>
          {t("weekly.hide")}
        </button>
      </div>
      <div className="ph-stats weekly-stats">
        <div><strong>{c.impressions}</strong><span>{t("weekly.impressions")} ({delta(c.impressions, p.impressions)})</span></div>
        <div><strong>{c.views}</strong><span>{t("weekly.views")} ({delta(c.views, p.views)})</span></div>
        <div><strong>{c.calls + c.whatsapp}</strong><span>{t("weekly.contacts")} ({delta(c.calls + c.whatsapp, p.calls + p.whatsapp)})</span></div>
        <div><strong>{c.requests}</strong><span>{t("weekly.requests")} ({delta(c.requests, p.requests)})</span></div>
      </div>
      <p className="help" style={{ marginTop: 0 }}>{t("weekly.compare")}</p>
      {todo.length === 0 ? <p className="ok">{t("weekly.nothing")}</p> : (
        <ul className="upkeep-list weekly-todo">
          {todo.map((x, i) => (
            <li key={i}>
              <span>{x.text}</span>
              <button type="button" className="chip" onClick={() => go(x.tab)}>{x.action}</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
