"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

/** Mon compte : déconnexion et suppression du compte sur demande (loi 18-07, section 10 du cahier). */
export default function Account() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setUser(session.user());
    setReady(true);
  }, []);

  async function remove() {
    if (!window.confirm(t("account.delete.confirm"))) return;
    try {
      await api("/auth/me", { method: "DELETE" });
      session.clear();
      setUser(null);
      setDone(true);
    } catch (e) {
      setError(e instanceof ApiError && e.message ? e.message : t("common.error"));
    }
  }

  if (!ready) return <p>{t("common.loading")}</p>;
  if (done) return (<section><h1>{t("account.title")}</h1><p className="ok" role="status">{t("account.deleted")}</p></section>);
  if (!user) {
    return (
      <section>
        <h1>{t("account.title")}</h1>
        <p>{t("account.loginFirst")}</p>
        <Link className="btn" href="/connexion?next=/compte">{t("nav.login")}</Link>
      </section>
    );
  }
  return (
    <section>
      <h1>{t("account.title")}</h1>
      <p><span className="meta">{t("account.phone")}</span><br /><strong>{user.phone}</strong></p>
      <p><span className="meta">{t("account.role")}</span><br /><strong>{t(`account.role.${user.role}`)}</strong></p>
      <div className="actions">
        <button className="btn btn-ghost" onClick={() => { session.clear(); setUser(null); }}>{t("nav.logout")}</button>
      </div>
      <h2 className="section">{t("account.delete.title")}</h2>
      <p className="help">{t("account.delete.text")}</p>
      {error && <p className="err" role="alert">{error}</p>}
      <div className="actions">
        <button className="btn" onClick={remove}>{t("account.delete.button")}</button>
      </div>
    </section>
  );
}
