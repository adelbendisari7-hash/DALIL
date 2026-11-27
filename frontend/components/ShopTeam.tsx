"use client";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";

type Member = { user_id: number; name: string | null; phone: string | null; permissions: string[]; status: string };
type Team = { manager: { name: string | null; phone: string }; members: Member[]; permissions: string[];
  templates: Record<string, string[]> };
type Activity = { at: string; who: string; action: string; label: string; target: string | null };

const errMsg = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));
const same = (a: string[], b: string[]) => a.length === b.length && a.every((x) => b.includes(x));

/** Équipe du magasin, réservée au gérant (plan côté magasin, phase 3) : il ajoute autant d'employés qu'il veut,
 * coche leurs accès, suspend, retire, passe la main. L'équipe DALIL n'y a pas accès. */
export default function ShopTeam({ shopId, onTransferred }: { shopId: number; onTransferred: () => void }) {
  const [team, setTeam] = useState<Team | null>(null);
  const [log, setLog] = useState<Activity[]>([]);
  const [phone, setPhone] = useState("");
  const [template, setTemplate] = useState("vendeur");
  const [to, setTo] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(() => {
    api<Team>(`/shops/${shopId}/team`).then(setTeam).catch(() => undefined);
    api<Activity[]>(`/shops/${shopId}/team/activity`).then(setLog).catch(() => undefined);
  }, [shopId]);
  useEffect(() => { load(); }, [load]);

  async function run(fn: () => Promise<unknown>, ok?: string) {
    setMsg(null);
    try {
      await fn();
      if (ok) setMsg({ ok: true, text: ok });
      load();
    } catch (e) {
      setMsg({ ok: false, text: errMsg(e) });
    }
  }

  const patch = (m: Member, json: Record<string, unknown>) =>
    run(() => api(`/shops/${shopId}/team/${m.user_id}`, { method: "PATCH", json }));
  const toggle = (m: Member, p: string) =>
    patch(m, { permissions: m.permissions.includes(p) ? m.permissions.filter((x) => x !== p) : [...m.permissions, p] });

  if (!team) return <p>{t("common.loading")}</p>;
  return (
    <>
      {msg && <p className={msg.ok ? "ok" : "err"} role={msg.ok ? "status" : "alert"}>{msg.text}</p>}

      <div className="card">
        <h2 className="card-title">{t("team.add.title")}</h2>
        <p className="help" style={{ marginTop: 0 }}>{t("team.add.help")}</p>
        <label htmlFor="tm-phone">{t("team.add.phone")}</label>
        <input id="tm-phone" type="tel" inputMode="tel" placeholder={t("login.phone.placeholder")} value={phone} onChange={(e) => setPhone(e.target.value)} />
        <span className="help">{t("team.add.template")}</span>
        <div className="chips">
          {Object.keys(team.templates).map((k) => (
            <button key={k} type="button" className="chip" aria-pressed={template === k} onClick={() => setTemplate(k)}>{t(`team.template.${k}`)}</button>
          ))}
        </div>
        <p className="help">{team.templates[template].map((p) => t(`team.perm.${p}`)).join(" · ")}</p>
        <div className="actions">
          <button type="button" className="btn" disabled={!phone.trim()} onClick={() => run(async () => {
            await api(`/shops/${shopId}/team`, { method: "POST", json: { phone, permissions: team.templates[template] } });
            setPhone("");
          }, t("team.add.done"))}>{t("team.add.button")}</button>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">{t("team.title", { n: team.members.length })}</h2>
        <p className="meta">{t("team.manager")} : {team.manager.name ?? team.manager.phone}</p>
        {team.members.length === 0 && <p className="help">{t("team.empty")}</p>}
        <ul className="list">
          {team.members.map((m) => {
            const tpl = Object.entries(team.templates).find(([, ps]) => same(ps, m.permissions))?.[0];
            return (
              <li key={m.user_id} className="member">
                <div style={{ width: "100%" }}>
                  <strong>{m.name ?? m.phone}</strong>{" "}
                  <span className="meta">{m.phone}</span>
                  {m.status === "suspended" && <span className="tag-demo">{t("team.suspended")}</span>}
                  <div className="chips" style={{ marginTop: "0.4rem" }}>
                    {Object.keys(team.templates).map((k) => (
                      <button key={k} type="button" className="chip chip-shortcut" aria-pressed={tpl === k}
                        onClick={() => patch(m, { permissions: team.templates[k] })}>{t(`team.template.${k}`)}</button>
                    ))}
                  </div>
                  <fieldset className="perms" style={{ border: 0, padding: 0, margin: "0.25rem 0 0" }}>
                    <legend className="sr-label">{t("team.perms", { name: m.name ?? "" })}</legend>
                    {team.permissions.map((p) => (
                      <label key={p} className="check">
                        <input type="checkbox" checked={m.permissions.includes(p)} onChange={() => toggle(m, p)} />
                        <span>{t(`team.perm.${p}`)}</span>
                      </label>
                    ))}
                  </fieldset>
                  <div className="actions" style={{ marginTop: "0.25rem" }}>
                    <button type="button" className="btn btn-ghost" onClick={() => patch(m, { status: m.status === "active" ? "suspended" : "active" })}>
                      {m.status === "active" ? t("team.suspend") : t("team.reactivate")}
                    </button>
                    <button type="button" className="btn btn-ghost" onClick={() => {
                      if (window.confirm(t("team.remove.confirm", { name: m.name ?? m.phone ?? "" })))
                        run(() => api(`/shops/${shopId}/team/${m.user_id}`, { method: "DELETE" }));
                    }}>{t("team.remove")}</button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </div>

      {team.members.length > 0 && (
        <div className="card">
          <h2 className="card-title">{t("team.transfer.title")}</h2>
          <p className="help" style={{ marginTop: 0 }}>{t("team.transfer.help")}</p>
          <label htmlFor="tr-to">{t("team.transfer.to")}</label>
          <select id="tr-to" value={to} onChange={(e) => setTo(e.target.value)}>
            <option value="">{t("vehicle.choose")}</option>
            {team.members.map((m) => <option key={m.user_id} value={m.user_id}>{m.name ?? m.phone}</option>)}
          </select>
          <label htmlFor="tr-pw">{t("team.transfer.password")}</label>
          <input id="tr-pw" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <div className="actions">
            <button type="button" className="btn btn-ghost" disabled={!to || !password} onClick={() => {
              if (!window.confirm(t("team.transfer.confirm"))) return;
              run(async () => {
                await api(`/shops/${shopId}/team/transfer`, { method: "POST", json: { user_id: Number(to), password } });
                onTransferred();
              });
            }}>{t("team.transfer.button")}</button>
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="card-title">{t("team.log.title")}</h2>
        {log.length === 0 && <p className="help">{t("team.log.empty")}</p>}
        <ul className="list activity">
          {log.map((a, i) => (
            <li key={i}>
              <span>
                <strong>{a.who}</strong> {a.label}{a.target ? ` : ${a.target}` : ""}
                <br /><span className="meta">{new Date(a.at).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" })}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
