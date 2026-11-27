"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

function Login() {
  const router = useRouter();
  const next = useSearchParams().get("next") || "/";
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [sent, setSent] = useState(false);
  const [consoleSms, setConsoleSms] = useState(false);
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const fail = (e: unknown) => setError(e instanceof ApiError && e.message ? e.message : t("common.error"));

  async function send(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await api<{ delivery?: string }>("/auth/otp/request", { method: "POST", json: { phone } });
      setConsoleSms(r.delivery === "console");
      setSent(true);
    } catch (err) { fail(err); }
    setBusy(false);
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      let r = await api<{ token: string; user: User }>("/auth/otp/verify", { method: "POST", json: { phone, code } });
      session.save(r.token, r.user);
      if (consent && !r.user.consent) {
        r = await api<{ token: string; user: User }>("/auth/me", { method: "PATCH", json: { consent: true } });
        session.save(r.token, r.user);
      }
      // Compte client pas encore complet (prénom, nom) : on le crée d'abord, puis retour là où il allait.
      // Pas pour l'espace magasin ni l'administration, qui ont leur propre parcours.
      if (r.user.role === "driver" && !r.user.complete && !/^\/(espace-magasin|admin)/.test(next)) {
        router.push(`/compte?bienvenue=1&next=${encodeURIComponent(next)}`);
      } else {
        router.push(next);
      }
    } catch (err) { fail(err); }
    setBusy(false);
  }

  return (
    <section style={{ maxWidth: "26rem" }}>
      <h1>{t("login.title")}</h1>
      <p>{t("login.lead")}</p>
      {!sent ? (
        <form onSubmit={send}>
          <label htmlFor="phone">{t("login.phone")}</label>
          <input id="phone" type="tel" inputMode="tel" autoComplete="tel" placeholder={t("login.phone.placeholder")} value={phone} onChange={(e) => setPhone(e.target.value)} required />
          <div className="actions"><button className="btn btn-block" disabled={busy}>{t("login.send")}</button></div>
        </form>
      ) : (
        <form onSubmit={verify}>
          {consoleSms && <p className="notice" role="note">{t("login.consoleHint")}</p>}
          <label htmlFor="code">{t("login.code")}</label>
          <input id="code" inputMode="numeric" autoComplete="one-time-code" maxLength={6} value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} required />
          <label className="check">
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} required />
            <span>{t("login.consent")}</span>
          </label>
          <div className="actions"><button className="btn btn-block" disabled={busy || !consent}>{t("login.verify")}</button></div>
        </form>
      )}
      {error && <p className="err" role="alert">{error}</p>}
    </section>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <Login />
    </Suspense>
  );
}
