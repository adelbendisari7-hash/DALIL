"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import ShopForm, { cleanShop, type ShopFormValue } from "@/components/ShopForm";
import { api, ApiError, session } from "@/lib/api";
import { t } from "@/lib/i18n";

/** Formulaire de collecte terrain sur téléphone (étape 4). La fiche est vérifiée d'office. */
export default function FieldForm() {
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [saved, setSaved] = useState<{ id: number; name: string } | null>(null);
  const [error, setError] = useState("");
  const [key, setKey] = useState(0);

  useEffect(() => setAllowed(session.user()?.role === "admin"), []);

  async function submit(v: ShopFormValue) {
    setError("");
    try {
      const r = await api<{ id: number; name: string }>("/admin/shops", { method: "POST", json: cleanShop(v) });
      setSaved(r);
      setKey((k) => k + 1);
      window.scrollTo({ top: 0 });
    } catch (e) {
      setError(e instanceof ApiError && e.message ? e.message : t("common.error"));
    }
  }

  if (allowed === null) return null;
  if (!allowed) return <p>{t("admin.forbidden")}</p>;
  return (
    <section>
      <Link href="/admin">{t("common.back")}</Link>
      <h1>{t("field.title")}</h1>
      <p>{t("field.lead")}</p>
      {saved && <p className="ok" role="status">{t("field.saved")} <Link href={`/magasins/${saved.id}`}>{saved.name}</Link></p>}
      {error && <p className="err" role="alert">{error}</p>}
      <ShopForm key={key} field submitLabel={t("field.submit")} onSubmit={submit} />
    </section>
  );
}
