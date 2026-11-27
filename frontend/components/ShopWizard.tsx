"use client";
import { useState } from "react";
import { IdentityFields, LocationFields, SellsFields, cleanShop, normalizeShop, type ShopFormValue } from "@/components/ShopForm";
import { api, ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";

type Nearby = { id: number; name: string; commune: string | null; address: string | null; distance_m: number | null; status: string };
const STEPS = ["identity", "location", "known", "sells", "recap"] as const;
type Step = (typeof STEPS)[number];

const errText = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));

/** Inscription d'un magasin en cinq étapes (objectif : moins de 3 minutes). L'étape « fiche déjà connue » propose de
 * revendiquer une fiche de l'équipe plutôt que de créer un doublon ; elle est sautée quand il n'y en a pas. */
export default function ShopWizard({ defaultPhone, onDone, becomeOwner }: {
  defaultPhone: string; onDone: (note?: string) => void; becomeOwner: () => Promise<void>;
}) {
  const [v, setV] = useState<ShopFormValue>(() => normalizeShop({ phone: defaultPhone }));
  const [step, setStep] = useState<Step>("identity");
  const [nearby, setNearby] = useState<Nearby[]>([]);
  const [error, setError] = useState("");
  const [claimable, setClaimable] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const set = <K extends keyof ShopFormValue>(k: K, val: ShopFormValue[K]) => setV((p) => ({ ...p, [k]: val }));
  const index = STEPS.indexOf(step);

  function canGo(): string {
    if (step === "identity" && v.name.trim().length < 2) return t("shop.wizard.needName");
    if (step === "location" && (v.lat == null || v.lng == null)) return t("shop.wizard.needPin");
    if (step === "sells" && !v.category_ids.length) return t("shop.wizard.needFamily");
    return "";
  }

  async function next() {
    const why = canGo();
    if (why) return setError(why);
    setError("");
    if (step === "location") {   // fiches de l'équipe proches ou au même numéro : étape suivante seulement s'il y en a
      setBusy(true);
      const q = new URLSearchParams({ lat: String(v.lat), lng: String(v.lng) });
      if (v.phone.trim()) q.set("phone", v.phone.trim());
      const found = await api<Nearby[]>(`/shops/nearby-claimable?${q}`).catch(() => []);
      setBusy(false);
      setNearby(found);
      return setStep(found.length ? "known" : "sells");
    }
    setStep(STEPS[index + 1]);
  }

  function back() {
    setError("");
    setStep(step === "sells" && !nearby.length ? "location" : STEPS[index - 1]);
  }

  async function claim(id: number) {
    setBusy(true);
    try {
      await becomeOwner();
      const r = await api<{ claim: string }>(`/shops/${id}/claim`, { method: "POST" });
      onDone(r.claim === "pending" ? t("shop.claim.pending") : t("shop.claim.accepted"));
    } catch (e) {
      setError(errText(e));
    }
    setBusy(false);
  }

  async function submit() {
    setBusy(true);
    setError("");
    try {
      await becomeOwner();
      await api("/shops", { method: "POST", json: cleanShop(v) });
      onDone();
    } catch (e) {
      if (e instanceof ApiError && e.code === "shop_phone_claimable") {
        setClaimable(typeof e.data?.shop_id === "number" ? e.data.shop_id : null);
      }
      setError(errText(e));
    }
    setBusy(false);
  }

  return (
    <div className="wizard card">
      <div className="wizard-progress" aria-hidden>
        {STEPS.map((s, i) => <span key={s} className={i <= index ? "done" : ""} />)}
      </div>
      <p className="meta" style={{ margin: "0 0 0.25rem" }}>{t("shop.wizard.step", { n: index + 1, total: STEPS.length })}</p>
      <h2 className="card-title">{t(`shop.wizard.${step}`)}</h2>
      <p className="help" style={{ marginTop: 0 }}>{t(`shop.wizard.${step}.help`)}</p>

      {step === "identity" && <IdentityFields v={v} set={set} showPhone />}
      {step === "location" && <LocationFields v={v} set={set} />}
      {step === "known" && (
        <ul className="list">
          {nearby.map((n) => (
            <li key={n.id}>
              <span>
                <strong>{n.name}</strong><br />
                <span className="meta">
                  {[n.address, n.commune].filter(Boolean).join(", ")}
                  {n.distance_m != null ? ` · ${t("shop.wizard.distance", { m: n.distance_m })}` : ""}
                </span>
              </span>
              <button type="button" className="btn" disabled={busy} onClick={() => claim(n.id)}>{t("shop.claim.button")}</button>
            </li>
          ))}
        </ul>
      )}
      {step === "sells" && <SellsFields v={v} set={set} />}
      {step === "recap" && (
        <dl className="recap">
          <dt>{t("shop.name")}</dt><dd>{v.name}</dd>
          <dt>{t("shop.phone")}</dt><dd>{v.phone || defaultPhone}</dd>
          <dt>{t("shops.address")}</dt><dd>{[v.address, v.landmark].filter(Boolean).join(" · ") || t("shop.wizard.pinOnly")}</dd>
          <dt>{t("shop.hours")}</dt><dd>{v.opening ? `${v.opening.days.length} ${t("shop.wizard.days")}, ${v.opening.from}-${v.opening.to}` : "—"}</dd>
          <dt>{t("shop.wizard.sells")}</dt>
          <dd>{t("shop.wizard.sellsCount", { brands: v.brand_ids.length, families: v.category_ids.length })}</dd>
        </dl>
      )}

      {error && <p className="err" role="alert">{error}</p>}
      {claimable != null && (
        <div className="actions"><button type="button" className="btn" disabled={busy} onClick={() => claim(claimable)}>{t("shop.claim.button")}</button></div>
      )}
      <div className="actions wizard-nav">
        {index > 0 && <button type="button" className="btn btn-ghost" onClick={back}>{t("shop.wizard.back")}</button>}
        {step === "known" && <button type="button" className="btn btn-ghost" onClick={() => setStep("sells")}>{t("shop.wizard.notMine")}</button>}
        {step === "recap" ? (
          <button type="button" className={`btn btn-primary${busy ? " is-busy" : ""}`} disabled={busy} onClick={submit}>{t("shop.register")}</button>
        ) : step !== "known" && (
          <button type="button" className={`btn${busy ? " is-busy" : ""}`} disabled={busy} onClick={next}>{t("shop.wizard.next")}</button>
        )}
      </div>
    </div>
  );
}
