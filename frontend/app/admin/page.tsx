"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, session } from "@/lib/api";
import { t } from "@/lib/i18n";

type Shop = { id: number; name: string; phone: string | null; commune: string | null; status: string; source: string; is_demo: boolean; owner_user_id: number | null };
type Metrics = {
  shops: { total: number; by_status: Record<string, number>; demo: number; with_owner: number };
  products: number; users: number;
  diagnoses: { total: number; last_30_days: number; by_status: Record<string, number> };
  contacts: { total: number; whatsapp: number; call: number };
  feedback: { part_found_rate: number | null; part_found_n: number; diagnosis_correct_rate: number | null; diagnosis_n: number };
  part_requests: number;
  top_contacted_parts: { part: string; count: number }[];
};
type Tab = "pending" | "verified" | "metrics" | "import";

const pct = (x: number | null) => (x == null ? "–" : `${Math.round(x * 100)} %`);

export default function Admin() {
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [tab, setTab] = useState<Tab>("pending");
  const [shops, setShops] = useState<Shop[]>([]);
  const [stale, setStale] = useState<Shop[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [msg, setMsg] = useState("");
  const [source, setSource] = useState("terrain");

  useEffect(() => setAllowed(session.user()?.role === "admin"), []);

  const load = useCallback(async () => {
    if (tab === "pending" || tab === "verified") {
      const st = tab === "pending" ? "draft" : "verified";
      setShops(await api<Shop[]>(`/admin/shops?status=${st}`).catch(() => []));
      if (tab === "verified") setStale(await api<Shop[]>("/admin/stale").catch(() => []));
    }
    if (tab === "metrics") setMetrics(await api<Metrics>("/admin/metrics").catch(() => null));
  }, [tab]);

  useEffect(() => { if (allowed) load(); }, [allowed, load]);

  async function act(id: number, action: "verify" | "reject") {
    await api(`/admin/shops/${id}/${action}`, { method: "POST" }).catch(() => undefined);
    load();
  }

  async function upload(path: string, e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    try {
      const r = await api<{ created: number; updated?: number; errors: { line: number; error: string }[] }>(path, { method: "POST", body: fd });
      setMsg(`${r.created} créés${r.updated != null ? `, ${r.updated} fusionnés` : ""}, ${r.errors.length} erreurs. ` +
        r.errors.slice(0, 5).map((x) => `Ligne ${x.line} : ${x.error}`).join(" ; "));
    } catch (err) {
      setMsg(err instanceof ApiError && err.message ? err.message : t("common.error"));
    }
    e.target.value = "";
  }

  if (allowed === null) return null;
  if (!allowed) return <p>{t("admin.forbidden")} <Link href="/connexion?next=/admin">{t("nav.login")}</Link></p>;

  return (
    <section>
      <h1>{t("admin.title")}</h1>
      <Link className="btn btn-primary" href="/admin/terrain">{t("admin.field")}</Link>
      <div className="tabs" role="tablist">
        {(["pending", "verified", "metrics", "import"] as Tab[]).map((k) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => { setTab(k); setMsg(""); }}>{t(`admin.tab.${k}`)}</button>
        ))}
      </div>

      {(tab === "pending" || tab === "verified") && (
        <>
          {shops.length === 0 && <p>{t("admin.empty")}</p>}
          <ul className="list">
            {shops.map((s) => (
              <li key={s.id}>
                <span>
                  <Link href={`/magasins/${s.id}`}>{s.name}</Link>
                  {s.is_demo && <span className="tag-demo">démo</span>}
                  <br />
                  <span className="meta">{[s.phone, s.commune, s.source].filter(Boolean).join(", ")}</span>
                </span>
                {tab === "pending" && (
                  <span className="actions" style={{ marginTop: 0 }}>
                    <button className="btn" onClick={() => act(s.id, "verify")}>{t("admin.verify")}</button>
                    <button className="btn btn-ghost" onClick={() => act(s.id, "reject")}>{t("admin.reject")}</button>
                  </span>
                )}
              </li>
            ))}
          </ul>
          {tab === "verified" && stale.length > 0 && (
            <>
              <h3 className="section">{t("admin.stale")}</h3>
              <ul className="list">{stale.map((s) => <li key={s.id}>{s.name}</li>)}</ul>
            </>
          )}
        </>
      )}

      {tab === "metrics" && metrics && (
        <>
          <div className="stats">
            <div><strong>{metrics.shops.total}</strong><span>magasins ({metrics.shops.demo} fictifs)</span></div>
            <div><strong>{metrics.shops.with_owner}</strong><span>magasins inscrits</span></div>
            <div><strong>{metrics.products}</strong><span>produits au catalogue</span></div>
            <div><strong>{metrics.diagnoses.total}</strong><span>diagnostics ({metrics.diagnoses.last_30_days} sur 30 jours)</span></div>
            <div><strong>{metrics.contacts.total}</strong><span>contacts ({metrics.contacts.whatsapp} WhatsApp)</span></div>
            <div><strong>{pct(metrics.feedback.part_found_rate)}</strong><span>pièce trouvée (n = {metrics.feedback.part_found_n})</span></div>
            <div><strong>{pct(metrics.feedback.diagnosis_correct_rate)}</strong><span>diagnostic jugé juste (n = {metrics.feedback.diagnosis_n})</span></div>
            <div><strong>{metrics.part_requests}</strong><span>demandes diffusées</span></div>
          </div>
          <h3>Diagnostics par résultat</h3>
          <ul className="list">
            {Object.entries(metrics.diagnoses.by_status).map(([k, n]) => <li key={k}><span>{k}</span><span>{n}</span></li>)}
          </ul>
          <h3 className="section">Pièces les plus demandées</h3>
          <ul className="list">
            {metrics.top_contacted_parts.map((p) => <li key={p.part}><span>{p.part}</span><span>{p.count}</span></li>)}
          </ul>
        </>
      )}

      {tab === "import" && (
        <>
          <label htmlFor="imp-src">{t("admin.import.source")}</label>
          <select id="imp-src" value={source} onChange={(e) => setSource(e.target.value)} style={{ maxWidth: "16rem" }}>
            <option value="terrain">terrain</option>
            <option value="osm">osm</option>
            <option value="declared">declared</option>
          </select>
          <label htmlFor="imp-shops">{t("admin.import.shops")}</label>
          <input id="imp-shops" type="file" accept=".csv,.xlsx" onChange={(e) => upload(`/admin/shops/import?source=${source}`, e)} />
          <p className="help">Colonnes : name, phone, whatsapp, commune, lat, lng, address, hours, brands, categories, parts_origin, sale_mode, osm_id. Listes séparées par « | ».</p>
          <label htmlFor="imp-refs">{t("admin.import.refs")}</label>
          <input id="imp-refs" type="file" accept=".csv,.xlsx" onChange={(e) => upload("/admin/part-references/import", e)} />
          <p className="help">Colonnes : famille, vehicule, reference, marque_piece, source.</p>
          {msg && <p className="help" role="status">{msg}</p>}
        </>
      )}
    </section>
  );
}
