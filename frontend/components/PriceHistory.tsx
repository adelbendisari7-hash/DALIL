"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Month = { month: string; products: number; shops: number; min: number | null; max: number | null; median: number | null };
type Cond = { min: number; median: number; max: number; products: number; shops: number };
type History = {
  demo: boolean; months: Month[]; now: Month; trend_pct: number | null; since: string | null;
  by_condition: Partial<Record<"neuf" | "adaptable" | "occasion", Cond>>;
};

const da = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} DA`;
const shops = (n: number) => (n === 1 ? t("prices.shop1") : t("prices.shopsN", { n }));
const monthName = (m: string) => new Date(`${m}-15`).toLocaleDateString("fr-FR", { month: "short" });

/** Historique des prix d'une pièce dans les catalogues des magasins (GET /prices/{id}) : chiffres d'aujourd'hui en tête,
 * puis une barre « du plus bas au plus haut » par mois, la médiane marquée d'un point. Une seule série : pas de
 * légende ; chaque mois porte son libellé au survol et au toucher, et les valeurs sont aussi écrites. */
export default function PriceHistory({ categoryId }: { categoryId: number }) {
  const [h, setH] = useState<History | null>(null);
  const [active, setActive] = useState<number | null>(null);

  useEffect(() => {
    api<History>(`/prices/${categoryId}`).then(setH).catch(() => setH(null));
  }, [categoryId]);

  if (!h || !h.now.products) return null;
  const months = h.months.filter((m) => m.products > 0);
  // Échelle resserrée sur les prix observés (barres d'intervalle, pas de longueurs : le zéro n'est pas nécessaire)
  const hiRaw = Math.max(...months.map((m) => m.max ?? 0));
  const loRaw = Math.min(...months.map((m) => m.min ?? Infinity));
  const pad = hiRaw === loRaw ? hiRaw * 0.1 : (hiRaw - loRaw) * 0.12;
  const hi = hiRaw + pad, lo = Math.max(0, loRaw - pad);
  const W = 300, H = 120, PAD_T = 10, PAD_B = 22, PAD_L = 44;
  const y = (v: number) => PAD_T + (1 - (v - lo) / (hi - lo)) * (H - PAD_T - PAD_B);
  const slot = (W - PAD_L) / h.months.length;
  const tick = (v: number) => Math.round(v).toLocaleString("fr-FR");
  const sel = active != null ? h.months[active] : null;

  return (
    <section className="card price-history" aria-labelledby="ph-title">
      <h2 id="ph-title" className="card-title">{t("prices.title")}</h2>
      {h.demo && <p className="tag-demo-note">{t("prices.demo")}</p>}
      <div className="ph-stats">
        <div><strong>{da(h.now.min!)}</strong><span>{t("prices.min")}</span></div>
        {h.now.median != null && <div><strong>{da(h.now.median)}</strong><span>{t("prices.median")}</span></div>}
        <div><strong>{h.now.shops}</strong><span>{t(h.now.shops === 1 ? "prices.tile.shop1" : "prices.tile.shops")}</span></div>
      </div>
      {h.trend_pct != null && (
        <p className="meta">
          {h.trend_pct === 0 ? t("prices.trend.flat", { since: monthName(h.since!) })
            : t(h.trend_pct > 0 ? "prices.trend.up" : "prices.trend.down", { n: Math.abs(h.trend_pct), since: monthName(h.since!) })}
        </p>
      )}

      {months.length > 1 && (
        <figure className="ph-chart">
          <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={t("prices.chart")} onMouseLeave={() => setActive(null)}>
            <line x1={PAD_L} x2={W} y1={H - PAD_B} y2={H - PAD_B} className="ph-axis" />
            {/* deux repères : le plus haut et le plus bas de la période */}
            {[hiRaw, loRaw].filter((v, i, a) => a.indexOf(v) === i).map((v) => (
              <g key={v}>
                <line x1={PAD_L} x2={W} y1={y(v)} y2={y(v)} className="ph-grid" />
                <text x={PAD_L - 4} y={y(v) + 3} textAnchor="end" className="ph-label">{tick(v)}</text>
              </g>
            ))}
            {h.months.map((m, i) => {
              const cx = PAD_L + slot * i + slot / 2;
              return (
                <g key={m.month} onMouseEnter={() => setActive(i)} onClick={() => setActive(active === i ? null : i)}
                   className={active === i ? "is-active" : undefined}>
                  <rect x={PAD_L + slot * i} y="0" width={slot} height={H} className="ph-hit" />
                  {m.min != null && m.max != null && m.max - m.min > 0 && (
                    <rect x={cx - 6} width="12" rx="4" y={y(m.max)} height={Math.max(8, y(m.min) - y(m.max))} className="ph-range" />
                  )}
                  {/* médiane (deux magasins ou plus) ; sinon un seul prix : un point */}
                  {(m.median != null || (m.min != null && m.min === m.max)) && (
                    <circle cx={cx} cy={y(m.median ?? m.min!)} r="5" className="ph-median" />
                  )}
                  <text x={cx} y={H - 6} textAnchor="middle" className="ph-label">{monthName(m.month)}</text>
                </g>
              );
            })}
          </svg>
          <figcaption className="meta" aria-live="polite">
            {sel && sel.min != null
              ? t("prices.month", { month: monthName(sel.month), min: da(sel.min), max: da(sel.max!), shops: shops(sel.shops) })
                + (sel.median != null ? ` · ${t("prices.median")} ${da(sel.median)}` : "")
              : t("prices.help")}
          </figcaption>
        </figure>
      )}

      <ul className="ph-conditions">
        {(["neuf", "adaptable", "occasion"] as const).map((c) => {
          const v = h.by_condition[c];
          return v ? (
            <li key={c}>
              <span>{t(`shop.condition.${c}`)}</span>
              <span className="meta">{v.min === v.max ? da(v.min) : `${da(v.min)} – ${da(v.max)}`} · {shops(v.shops)}</span>
            </li>
          ) : null;
        })}
      </ul>
      <p className="help">{t("prices.note")}</p>
    </section>
  );
}
