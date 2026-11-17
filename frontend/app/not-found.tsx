import Link from "next/link";
import { t } from "@/lib/i18n";

/** Page 404 en français (sans elle, Next.js affiche « This page could not be found. »). */
export default function NotFound() {
  return (
    <section>
      <h1>{t("common.notFound.title")}</h1>
      <p>{t("common.notFound.text")}</p>
      <p><Link className="btn" href="/">{t("common.home")}</Link></p>
    </section>
  );
}
