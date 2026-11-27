"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api, session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

/** Icônes au trait (24 px), dessinées ici : aucune bibliothèque à télécharger. */
const ICONS: Record<string, React.ReactNode> = {
  diagnose: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 12h4l2.5-6 4 12 2.5-6H21" />
    </svg>
  ),
  parts: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="3.2" />
      <path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1" />
    </svg>
  ),
  shop: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M4 9.5V20h16V9.5" />
      <path d="M2.5 9.5 4.5 4h15l2 5.5c0 1.4-1.3 2.5-2.9 2.5s-2.9-1.1-2.9-2.5c0 1.4-1.3 2.5-2.9 2.5S9.9 10.9 9.9 9.5C9.9 10.9 8.6 12 7 12s-2.9-1.1-2.9-2.5" />
      <path d="M10 20v-5h4v5" />
    </svg>
  ),
  account: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" />
    </svg>
  ),
  admin: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M12 2.5 4 5.5v6c0 5 3.4 8.6 8 10 4.6-1.4 8-5 8-10v-6z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  ),
};

/** Barre du haut (matériau translucide) ; la navigation devient une barre d'onglets en bas sur téléphone. */
export default function TopBar() {
  const path = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [online, setOnline] = useState(true);
  const [pending, setPending] = useState(0);

  // Demandes de clients en attente de réponse (gérant ou employé qui y répond) : relu à chaque page et toutes les minutes
  useEffect(() => {
    if (!user || (user.role !== "shop_owner" && user.role !== "admin" && user.role !== "driver")) return setPending(0);
    let stop = false;
    const read = () => api<{ pending: number }>("/part-requests/pending-count")
      .then((r) => { if (!stop) setPending(r.pending); }).catch(() => undefined);
    read();
    const id = setInterval(read, 60_000);
    return () => { stop = true; clearInterval(id); };
  }, [user, path]);

  useEffect(() => {
    const sync = () => setUser(session.user());
    sync();
    window.addEventListener("dalil-auth", sync);
    const on = () => setOnline(navigator.onLine);
    on();
    window.addEventListener("online", on);
    window.addEventListener("offline", on);
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }
    return () => {
      window.removeEventListener("dalil-auth", sync);
      window.removeEventListener("online", on);
      window.removeEventListener("offline", on);
    };
  }, []);

  // Le nom complet sert d'étiquette (lecteurs d'écran, tests) ; le libellé court s'affiche sous l'icône sur téléphone.
  const link = (href: string, icon: string, long: string, short: string, count = 0) => {
    const current = path === href || (href !== "/" && path.startsWith(href)) || (href === "/" && path.startsWith("/diagnostic"));
    return (
      <Link href={href} aria-label={count ? `${long} (${t("nav.pending", { n: count })})` : long}
        aria-current={current ? "page" : undefined}>
        <span className="nav-icon">{ICONS[icon]}{count > 0 && <span className="nav-badge" aria-hidden>{count > 9 ? "9+" : count}</span>}</span>
        <span className="label-long">{long}</span>
        <span className="label-short">{short}</span>
      </Link>
    );
  };

  return (
    <header className="topbar">
      {!online && <div className="offline" role="status">{t("common.offline")}</div>}
      <div className="topbar-inner">
        <Link href="/" className="brand" aria-label={t("nav.home")}>
          {t("app.name")}
        </Link>
        <nav className="nav">
          {link("/", "diagnose", t("nav.diagnose"), t("nav.diagnose"))}
          {link("/pieces", "parts", t("nav.parts"), t("nav.parts.short"))}
          {link("/espace-magasin", "shop", t("nav.shop"), t("nav.shop.short"), pending)}
          {user?.role === "admin" && link("/admin", "admin", t("nav.admin"), t("nav.admin.short"))}
          {user
            ? link("/compte", "account", t("nav.account"), t("nav.account.short"))
            : link("/connexion", "account", t("nav.login"), t("nav.login"))}
        </nav>
      </div>
    </header>
  );
}
