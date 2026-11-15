"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { session, type User } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function TopBar() {
  const path = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [online, setOnline] = useState(true);

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

  const link = (href: string, label: string) => (
    <Link href={href} aria-current={path === href || (href !== "/" && path.startsWith(href)) ? "page" : undefined}>
      {label}
    </Link>
  );

  return (
    <header className="topbar">
      {!online && <div className="offline">{t("common.offline")}</div>}
      <div className="topbar-inner">
        <Link href="/" className="brand" aria-label={t("nav.home")}>
          {t("app.name")}
        </Link>
        <nav className="nav">
          {link("/", t("nav.diagnose"))}
          {link("/pieces", t("nav.parts"))}
          {link("/espace-magasin", t("nav.shop"))}
          {user?.role === "admin" && link("/admin", t("nav.admin"))}
          {user ? (
            <button onClick={() => session.clear()}>{t("nav.logout")}</button>
          ) : (
            link("/connexion", t("nav.login"))
          )}
        </nav>
      </div>
    </header>
  );
}
