"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, session } from "@/lib/api";
import { t } from "@/lib/i18n";
import type { Watch } from "@/components/PriceWatches";

/** « Suivre le prix » d'une pièce : DALIL prévient quand le prix le plus bas baisse, ou dès qu'un magasin la propose.
 * Sans compte : lien vers la connexion, qui ramène ici. */
export default function PriceFollow({ categoryId, variantId }: { categoryId: number; variantId?: number }) {
  const [logged, setLogged] = useState(false);
  const [watch, setWatch] = useState<Watch | null | undefined>(undefined);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const on = !!session.token();
    setLogged(on);
    if (!on) return setWatch(null);
    api<Watch[]>("/me/price-watches").then((ws) => setWatch(ws.find((w) => w.category_id === categoryId) ?? null))
      .catch(() => setWatch(null));
  }, [categoryId]);

  async function follow() {
    setBusy(true);
    try {
      setWatch(await api<Watch>("/me/price-watches", { method: "POST", json: { category_id: categoryId, variant_id: variantId ?? null } }));
    } catch { /* message générique inutile : le bouton reste disponible */ }
    setBusy(false);
  }
  async function stop() {
    if (!watch) return;
    setBusy(true);
    await api(`/me/price-watches/${watch.id}`, { method: "DELETE" }).catch(() => undefined);
    setWatch(null);
    setBusy(false);
  }

  if (watch === undefined) return null;
  const here = typeof window !== "undefined" ? window.location.pathname + window.location.search : "/";
  return (
    <div className="price-follow">
      {!logged ? (
        <p className="help"><Link href={`/connexion?next=${encodeURIComponent(here)}`}>{t("watch.login")}</Link></p>
      ) : watch ? (
        <p className="help" role="status">
          <span className="ok">{t("watch.following")}</span>{" "}
          <button type="button" className="chip" onClick={stop} disabled={busy}>{t("watch.stop")}</button>
        </p>
      ) : (
        <button type="button" className="btn btn-ghost" onClick={follow} disabled={busy}>{t("watch.follow")}</button>
      )}
    </div>
  );
}
