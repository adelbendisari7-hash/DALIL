"use client";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";

type QShop = {
  id: number; name: string; phone: string | null; address: string | null; landmark: string | null; commune: string | null;
  hours: string | null; created_at?: string; owner: { name: string | null; phone: string } | null;
  duplicates: { id: number; name: string; phone: string | null }[];
};
type QClaim = { id: number; shop: { id: number; name: string; phone: string | null; commune: string | null };
  user: { name: string | null; phone: string } };

const CHECKS = ["phone_ok", "address_ok", "activity_ok"] as const;

/** File « Magasins à vérifier » (vérification par appel, décision du 27/11/2026). */
export default function VerificationQueue() {
  const [data, setData] = useState<{ shops: QShop[]; claims: QClaim[] } | null>(null);
  const [checks, setChecks] = useState<Record<number, Record<string, boolean>>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [msg, setMsg] = useState("");

  const load = useCallback(() => {
    api<{ shops: QShop[]; claims: QClaim[] }>("/admin/verification").then(setData).catch(() => setData({ shops: [], claims: [] }));
  }, []);
  useEffect(() => { load(); }, [load]);

  async function act(path: string, json?: unknown) {
    setMsg("");
    try {
      await api(path, { method: "POST", json });
      load();
    } catch (e) {
      setMsg(e instanceof ApiError && e.message ? e.message : t("common.error"));
    }
  }

  const tick = (id: number, k: string, v: boolean) => setChecks({ ...checks, [id]: { ...(checks[id] ?? {}), [k]: v } });
  const call = (phone: string | null) => phone && <a className="btn" href={`tel:${phone}`}>{t("admin.verify.call")} {phone}</a>;

  if (!data) return <p>{t("common.loading")}</p>;
  return (
    <>
      {msg && <p className="err" role="alert">{msg}</p>}
      {data.shops.length === 0 && data.claims.length === 0 && <p className="help">{t("admin.verify.empty")}</p>}

      {data.shops.map((s) => {
        const c = checks[s.id] ?? {};
        const all = CHECKS.every((k) => c[k]);
        const reason = reasons[`s${s.id}`] ?? "";
        return (
          <div key={s.id} className="card">
            <h3 className="card-title">{s.name}</h3>
            <p className="meta">
              {[s.address, s.landmark, s.commune].filter(Boolean).join(" · ")}
              {s.hours ? ` · ${s.hours}` : ""}
              {s.owner ? <><br />{t("admin.verify.owner")} : {s.owner.name ?? "?"} ({s.owner.phone})</> : null}
            </p>
            {s.duplicates.length > 0 && (
              <p className="notice">{t("admin.verify.duplicates")} : {s.duplicates.map((d) => `${d.name}${d.phone ? ` (${d.phone})` : ""}`).join(", ")}</p>
            )}
            <div className="actions">{call(s.phone)}</div>
            <fieldset style={{ border: 0, padding: 0, margin: "0.5rem 0 0" }}>
              <legend className="help">{t("admin.verify.checklist")}</legend>
              {CHECKS.map((k) => (
                <label key={k} className="check">
                  <input type="checkbox" checked={Boolean(c[k])} onChange={(e) => tick(s.id, k, e.target.checked)} />
                  <span>{t(`admin.verify.${k}`)}</span>
                </label>
              ))}
            </fieldset>
            <div className="actions">
              <button className="btn" disabled={!all} onClick={() => act(`/admin/shops/${s.id}/verify`, { phone_ok: true, address_ok: true, activity_ok: true })}>
                {t("admin.verify.accept")}
              </button>
            </div>
            <label htmlFor={`rj-${s.id}`}>{t("admin.verify.reason")}</label>
            <div className="actions" style={{ marginTop: 0, flexWrap: "nowrap" }}>
              <input id={`rj-${s.id}`} maxLength={255} placeholder={t("admin.verify.reason.placeholder")} value={reason}
                onChange={(e) => setReasons({ ...reasons, [`s${s.id}`]: e.target.value })} />
              <button className="btn btn-ghost" disabled={reason.trim().length < 3}
                onClick={() => act(`/admin/shops/${s.id}/reject`, { reason: reason.trim() })}>{t("admin.verify.reject")}</button>
            </div>
          </div>
        );
      })}

      {data.claims.length > 0 && <h2 className="section">{t("admin.verify.claims")}</h2>}
      {data.claims.map((c) => {
        const reason = reasons[`c${c.id}`] ?? "";
        return (
          <div key={c.id} className="card">
            <h3 className="card-title">{c.shop.name}</h3>
            <p className="meta">{t("admin.verify.claimBy")} {c.user.name ?? "?"} ({c.user.phone}){c.shop.commune ? ` · ${c.shop.commune}` : ""}</p>
            <p className="help">{t("admin.verify.claimHelp")}</p>
            <div className="actions">
              {call(c.shop.phone)}
              <button className="btn" onClick={() => act(`/admin/claims/${c.id}/accept`)}>{t("admin.verify.claimAccept")}</button>
            </div>
            <div className="actions" style={{ flexWrap: "nowrap" }}>
              <input aria-label={t("admin.verify.reason")} maxLength={255} placeholder={t("admin.verify.reason.placeholder")} value={reason}
                onChange={(e) => setReasons({ ...reasons, [`c${c.id}`]: e.target.value })} />
              <button className="btn btn-ghost" disabled={reason.trim().length < 3}
                onClick={() => act(`/admin/claims/${c.id}/reject`, { reason: reason.trim() })}>{t("admin.verify.reject")}</button>
            </div>
          </div>
        );
      })}
    </>
  );
}
