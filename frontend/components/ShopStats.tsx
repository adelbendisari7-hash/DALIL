"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

type Period = {
  impressions: number; views: number; calls: number; whatsapp: number; requests: number; answered: number;
  response_minutes: number | null; found_yes: number; found_no: number;
};
type Stats = { days: number; current: Period; previous: Period; fast_reply: boolean;
  demand: { category_id: number; name: string; searches: number; sold: boolean }[] };

const TILES: (keyof Period)[] = ["impressions", "views", "calls", "whatsapp", "requests", "answered"];

function Delta({ now, before }: { now: number; before: number }) {
  if (now === before) return <span className="delta">=</span>;
  const up = now > before;
  return <span className={`delta ${up ? "up" : "down"}`}>{up ? "▲" : "▼"} {Math.abs(now - before)}</span>;
}

function duration(min: number | null): string {
  if (min == null) return "—";
  if (min < 60) return t("stats.minutes", { n: min });
  return t("stats.hours", { n: Math.round(min / 6) / 10 });
}

/** Tableau de bord du magasin (plan côté magasin, phase 4) : 30 derniers jours, comparés aux 30 précédents. */
export default function ShopStats({ shopId, onEditProfile }: { shopId: number; onEditProfile?: () => void }) {
  const [s, setS] = useState<Stats | null>(null);
  useEffect(() => { api<Stats>(`/shops/${shopId}/stats`).then(setS).catch(() => undefined); }, [shopId]);
  if (!s) return <p>{t("common.loading")}</p>;
  const c = s.current;
  const p = s.previous;
  const found = c.found_yes + c.found_no;
  const missing = s.demand.filter((d) => !d.sold);
  return (
    <>
      <div className="card">
        <h2 className="card-title">{t("stats.title", { n: s.days })}</h2>
        {s.fast_reply && <p className="badge-verified badge-fast">{t("stats.fast")}</p>}
        <div className="stats">
          {TILES.map((k) => (
            <div key={k}>
              <strong>{c[k] ?? 0}</strong>
              <span>{t(`stats.${k}`)}</span>
              <Delta now={(c[k] as number) ?? 0} before={(p[k] as number) ?? 0} />
            </div>
          ))}
          <div>
            <strong>{duration(c.response_minutes)}</strong>
            <span>{t("stats.response")}</span>
          </div>
          <div>
            <strong>{found ? `${Math.round((100 * c.found_yes) / found)} %` : "—"}</strong>
            <span>{t("stats.found", { n: found })}</span>
          </div>
        </div>
        <p className="help">{t("stats.help")}</p>
      </div>

      <div className="card">
        <h2 className="card-title">{t("stats.demand.title")}</h2>
        <p className="help" style={{ marginTop: 0 }}>{t("stats.demand.help")}</p>
        {s.demand.length === 0 && <p className="help">{t("stats.demand.empty")}</p>}
        <ul className="list">
          {s.demand.map((d) => (
            <li key={d.category_id}>
              <span><strong>{d.name}</strong><br /><span className="meta">{t("stats.demand.searches", { n: d.searches })}</span></span>
              {d.sold ? <span className="badge-verified">{t("stats.demand.sold")}</span>
                : <span className="open-pill">{t("stats.demand.notSold")}</span>}
            </li>
          ))}
        </ul>
        {missing.length > 0 && onEditProfile && (
          <div className="notice">
            {t("stats.demand.tip", { n: missing.length })}{" "}
            <button type="button" className="btn btn-ghost" onClick={onEditProfile}>{t("stats.demand.edit")}</button>
          </div>
        )}
      </div>
    </>
  );
}
