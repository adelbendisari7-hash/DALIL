"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import ShopContact, { type ContactShop } from "@/components/ShopContact";
import { api, requestStore, session } from "@/lib/api";
import { t } from "@/lib/i18n";

type Answer = { shop: ContactShop & { commune: string | null; verified?: boolean }; available: boolean; price: number | null; responded_at: string };
type Req = { id: number; created_at: string; part: string | null; vehicle: string | null; category_id: number; variant_id: number | null;
  notified: number; answered: number; unseen: number; responses: Answer[]; photo_url?: string | null };

/** « Mes demandes » : réponses des magasins (disponible, prix), du moins cher au plus cher, avec appel et WhatsApp.
 * Connecté : les demandes du compte ; sans compte : celles envoyées depuis ce téléphone (jeton secret). */
export default function MyRequests() {
  const [reqs, setReqs] = useState<Req[] | null>(null);

  useEffect(() => {
    (async () => {
      const mine = session.token() ? await api<Req[]>("/me/part-requests").catch(() => []) : [];
      const known = new Set(mine.map((r) => r.id));
      const local = await Promise.all(requestStore.list().filter((r) => !known.has(r.id)).map((r) =>
        api<Req>(`/part-requests/${r.id}?token=${encodeURIComponent(r.token)}`).catch(() => null)));
      const all = [...mine, ...local.filter((r): r is Req => r !== null)].sort((a, b) => b.id - a.id);
      setReqs(all);
      // Réponses lues : le repère de l'onglet Compte disparaît
      const tokens = new Map(requestStore.list().map((r) => [r.id, r.token]));
      for (const r of all.filter((x) => x.unseen > 0)) {
        const q = tokens.get(r.id) ? `?token=${encodeURIComponent(tokens.get(r.id)!)}` : "";
        api(`/part-requests/${r.id}/seen${q}`, { method: "POST" }).catch(() => undefined);
      }
      window.dispatchEvent(new Event("dalil-requests-seen"));
    })();
  }, []);

  if (!reqs) return <p>{t("common.loading")}</p>;
  return (
    <section>
      <h1>{t("requests.title")}</h1>
      <p className="lead">{t("requests.lead")}</p>
      {reqs.length === 0 && (
        <div className="card">
          <p>{t("requests.empty")}</p>
          <Link className="btn" href="/pieces">{t("home.mechanic.link")}</Link>
        </div>
      )}
      {reqs.map((r) => {
        const ctx = { categoryId: r.category_id, variantId: r.variant_id ?? undefined, partName: r.part ?? "" };
        const best = r.responses.find((a) => a.available);
        return (
          <article key={r.id} className="card request">
            <div className="status-head">
              <h2 className="card-title" style={{ margin: 0 }}>{r.part}</h2>
              {r.unseen > 0 && <span className="badge-verified badge-new">{t("requests.new", { n: r.unseen })}</span>}
            </div>
            <p className="meta">
              {[r.vehicle, new Date(r.created_at).toLocaleDateString("fr-FR")].filter(Boolean).join(" · ")}
              {" · "}{t("requests.progress", { notified: r.notified, answered: r.answered })}
            </p>
            {r.photo_url && (
              <a href={r.photo_url} target="_blank" rel="noopener noreferrer" className="request-photo">
                <img src={r.photo_url} alt={t("requests.photo.alt")} className="thumb thumb-large" loading="lazy" />
              </a>
            )}
            {r.answered === 0 && <p className="help">{t("requests.waiting")}</p>}
            <ul className="shops">
              {r.responses.map((a) => (
                <li key={a.shop.id} className={`shop answer${a.available ? "" : " is-out"}${a === best ? " is-best" : ""}`}>
                  <div className="status-head">
                    <h3><Link href={`/magasins/${a.shop.id}`}>{a.shop.name}</Link></h3>
                    {a.available
                      ? <strong className="answer-price">{a.price != null ? `${a.price.toLocaleString("fr-FR")} DA` : t("requests.available")}</strong>
                      : <span className="open-pill">{t("shop.inbox.unavailable")}</span>}
                  </div>
                  {a === best && r.responses.filter((x) => x.available).length > 1 && <span className="cause-badge">{t("requests.cheapest")}</span>}
                  <span className="meta">{a.shop.commune}</span>
                  {a.available && <ShopContact shop={a.shop} ctx={ctx} />}
                </li>
              ))}
            </ul>
          </article>
        );
      })}
    </section>
  );
}
