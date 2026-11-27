"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { api, ApiError, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

type Saved = { token: string; user: User };

/** Champ de mot de passe avec bouton « Afficher » (saisie sur un petit écran tactile). */
function PasswordInput({ id, value, onChange, autoComplete }: { id: string; value: string; onChange: (v: string) => void; autoComplete: string }) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ display: "flex", gap: "0.5rem" }}>
      <input id={id} type={show ? "text" : "password"} autoComplete={autoComplete} maxLength={128} required value={value}
        onChange={(e) => onChange(e.target.value)} />
      <button type="button" className="btn btn-ghost" onClick={() => setShow(!show)} aria-controls={id}>
        {show ? t("login.password.hide") : t("login.password.show")}
      </button>
    </div>
  );
}

/** Connexion et inscription par mot de passe (les SMS sont payants : la vérification par SMS reviendra plus tard). */
function Login() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/";
  const [mode, setMode] = useState<"login" | "register">(params.get("inscription") === "1" ? "register" : "login");
  const [f, setF] = useState({ first_name: "", last_name: "", phone: "", password: "", email: "" });
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });

  function go(user: User, registered: boolean) {
    // Compte client à compléter (prénom, nom) ou tout juste créé : page du compte (voitures), puis retour où il allait.
    // Pas pour l'espace magasin ni l'administration, qui ont leur propre parcours.
    const ownFlow = /^\/(espace-magasin|admin)/.test(next);
    if (user.role === "driver" && !ownFlow && (registered || !user.complete || !user.has_password)) {
      router.push(`/compte?bienvenue=1&next=${encodeURIComponent(next)}`);
    } else {
      router.push(next);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = mode === "login"
        ? await api<Saved>("/auth/login", { method: "POST", json: { phone: f.phone, password: f.password } })
        : await api<Saved>("/auth/register", { method: "POST", json: { ...f, email: f.email || null, consent } });
      session.save(r.token, r.user);
      go(r.user, mode === "register");
    } catch (err) {
      setError(err instanceof ApiError && err.message ? err.message : t("common.error"));
      setBusy(false);
    }
  }

  const switchTo = (m: "login" | "register") => { setMode(m); setError(""); };
  return (
    <section className="auth">
      <h1>{mode === "login" ? t("login.title") : t("login.tab.register")}</h1>
      <div className="tabs" role="tablist">
        <button role="tab" type="button" aria-selected={mode === "login"} onClick={() => switchTo("login")}>{t("login.tab.login")}</button>
        <button role="tab" type="button" aria-selected={mode === "register"} onClick={() => switchTo("register")}>{t("login.tab.register")}</button>
      </div>
      <form className="card" onSubmit={submit} noValidate>
        <p className="help" style={{ marginTop: 0 }}>{mode === "login" ? t("login.lead") : t("login.register.lead")}</p>
        {mode === "register" && (
          <div className="row">
            <div>
              <label htmlFor="first_name">{t("account.firstName")}</label>
              <input id="first_name" autoComplete="given-name" maxLength={60} required value={f.first_name} onChange={set("first_name")} />
            </div>
            <div>
              <label htmlFor="last_name">{t("account.lastName")}</label>
              <input id="last_name" autoComplete="family-name" maxLength={60} required value={f.last_name} onChange={set("last_name")} />
            </div>
          </div>
        )}
        <label htmlFor="phone">{t("login.phone")}</label>
        <input id="phone" type="tel" inputMode="tel" autoComplete="tel" placeholder={t("login.phone.placeholder")} required
          value={f.phone} onChange={set("phone")} />
        <label htmlFor="password">{mode === "login" ? t("login.password") : t("login.password.new")}</label>
        <PasswordInput id="password" value={f.password} onChange={(v) => setF({ ...f, password: v })}
          autoComplete={mode === "login" ? "current-password" : "new-password"} />
        {mode === "register" && (
          <>
            <label htmlFor="email">{t("account.email")} <span className="meta">({t("account.optional")})</span></label>
            <input id="email" type="email" inputMode="email" autoComplete="email" maxLength={160} value={f.email} onChange={set("email")} />
            <label className="check">
              <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} required />
              <span>{t("login.consent")}</span>
            </label>
          </>
        )}
        {error && <p className="err" role="alert">{error}</p>}
        <div className="actions">
          <button className="btn btn-block" disabled={busy || (mode === "register" && !consent)}>
            {mode === "login" ? t("login.submit") : t("login.register.submit")}
          </button>
        </div>
      </form>
      {mode === "login" && <p className="help section">{t("login.forgot")}</p>}
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
