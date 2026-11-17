"use client";
import { useState } from "react";
import { api, vehicleStore } from "@/lib/api";
import { t } from "@/lib/i18n";

export type ContactShop = { id: number; name: string; phone: string | null; whatsapp: string | null; is_demo: boolean };
type Ctx = { categoryId?: number; variantId?: number; sessionId?: number; partName?: string };

/** Appel et WhatsApp avec message pré-rempli (F8), puis question « pièce trouvée ? » (F9). */
export default function ShopContact({ shop, ctx }: { shop: ContactShop; ctx: Ctx }) {
  const [contacted, setContacted] = useState(false);
  const [answered, setAnswered] = useState(false);
  const [demoNote, setDemoNote] = useState(false);

  async function log(channel: "call" | "whatsapp") {
    await api("/contact-events", {
      method: "POST",
      json: { shop_id: shop.id, channel, category_id: ctx.categoryId ?? null, variant_id: ctx.variantId ?? null, session_id: ctx.sessionId ?? null },
    }).catch(() => undefined);
    setContacted(true);
  }

  function open(channel: "call" | "whatsapp", e: React.MouseEvent) {
    log(channel);
    if (shop.is_demo) {
      e.preventDefault();
      setDemoNote(true);
    }
  }

  async function found(yes: boolean) {
    await api("/feedback", {
      method: "POST",
      json: { shop_id: shop.id, category_id: ctx.categoryId ?? null, session_id: ctx.sessionId ?? null, part_found: yes },
    }).catch(() => undefined);
    setAnswered(true);
  }

  const vehicle = vehicleStore.get()?.label || t("shops.whatsapp.noVehicle");
  const msg = t("shops.whatsapp.msg", { part: (ctx.partName || "").toLowerCase(), vehicle });
  const wa = shop.whatsapp ? `https://wa.me/${shop.whatsapp.replace("+", "")}?text=${encodeURIComponent(msg)}` : null;
  // Magasin fictif : aucun numéro dans le lien (un appui long sur le téléphone pourrait sinon le composer, et un
  // numéro de démonstration au format algérien peut appartenir à quelqu'un).
  const callHref = shop.is_demo ? "#" : `tel:${shop.phone}`;
  const waHref = shop.is_demo ? "#" : wa;

  return (
    <div>
      <div className="actions">
        {shop.phone && (
          <a className="btn" href={callHref} onClick={(e) => open("call", e)}>{t("shops.call")}</a>
        )}
        {wa && (
          <a className="btn btn-wa" href={waHref ?? undefined} target="_blank" rel="noopener noreferrer" onClick={(e) => open("whatsapp", e)}>
            {t("shops.whatsapp")}
          </a>
        )}
      </div>
      {demoNote && <p className="help" role="status">{t("shops.demo.blocked")}</p>}
      {contacted && ctx.categoryId && (
        <div className="found">
          {answered ? (
            <span className="ok">{t("shops.found.thanks")}</span>
          ) : (
            <>
              <span>{t("shops.found.q", { name: shop.name })} </span>
              <button className="chip" onClick={() => found(true)}>{t("shops.found.yes")}</button>{" "}
              <button className="chip" onClick={() => found(false)}>{t("shops.found.no")}</button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
