"use client";
import { useEffect, useState } from "react";
import { api, ApiError, type UserCar } from "@/lib/api";
import { t } from "@/lib/i18n";

type Pending = { id: number; status: string; include_prices: boolean; expires_at: string; code?: string };
type Preview = { vehicle: string; mileage_km: number | null; visits: number; last_visit: string | null; controles: number;
  include_prices: boolean; expires_at: string };

const day = (iso: string) => new Date(iso).toLocaleDateString("fr-FR");
const errMsg = (e: unknown) => (e instanceof ApiError && e.message ? e.message : t("common.error"));

/** Vendeur : code pour transmettre la voiture et son carnet à l'acheteur (seulement s'il le décide). */
export function TransferPanel({ car }: { car: UserCar }) {
  const [pending, setPending] = useState<Pending | null | undefined>(undefined);
  const [prices, setPrices] = useState(false);
  const [shared, setShared] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api<Pending | null>(`/me/vehicles/${car.id}/transfer`).then(setPending).catch(() => setPending(null));
  }, [car.id]);

  async function create() {
    setMsg("");
    try {
      setPending(await api<Pending>(`/me/vehicles/${car.id}/transfer`, { method: "POST", json: { include_prices: prices } }));
    } catch (e) { setMsg(errMsg(e)); }
  }
  async function cancel() {
    await api(`/me/vehicles/${car.id}/transfer`, { method: "DELETE" }).catch(() => undefined);
    setPending(null);
  }
  async function share(p: Pending) {
    const text = t("transfer.shareText", { code: p.code ?? "", date: day(p.expires_at) });
    if (navigator.share) { await navigator.share({ title: "DALIL", text }).catch(() => undefined); return; }
    try { await navigator.clipboard.writeText(text); setShared(true); }
    catch { window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank", "noopener"); }
  }

  if (pending === undefined) return <p>{t("common.loading")}</p>;
  return (
    <div className="maintenance transfer">
      <p style={{ marginTop: 0 }}>{t("transfer.intro")}</p>
      <ul className="transfer-list">
        <li>{t("transfer.passes")}</li>
        <li>{t("transfer.stays")}</li>
      </ul>
      {pending?.code ? (
        <div className="transfer-code-box" role="status">
          <span className="meta">{t("transfer.codeLabel")}</span>
          <strong className="transfer-code">{pending.code}</strong>
          <span className="meta">{t("transfer.until", { date: day(pending.expires_at) })}{pending.include_prices ? ` · ${t("transfer.withPrices")}` : ""}</span>
          <div className="actions">
            <button type="button" className="btn" onClick={() => share(pending)}>{t("transfer.share")}</button>
            <button type="button" className="btn btn-ghost" onClick={cancel}>{t("transfer.cancel")}</button>
          </div>
          {shared && <span className="ok">{t("result.share.copied")}</span>}
          <p className="help">{t("transfer.codeOnce")}</p>
        </div>
      ) : (
        <>
          {pending && (
            <p className="notice">{t("transfer.pending", { date: day(pending.expires_at) })}{" "}
              <button type="button" className="chip" onClick={cancel}>{t("transfer.cancel")}</button></p>
          )}
          <label className="check">
            <input type="checkbox" checked={prices} onChange={(e) => setPrices(e.target.checked)} />
            <span>{t("transfer.includePrices")}</span>
          </label>
          <button type="button" className="btn" onClick={create}>{t(pending ? "transfer.newCode" : "transfer.create")}</button>
        </>
      )}
      {msg && <p className="err" role="alert">{msg}</p>}
    </div>
  );
}

/** Acheteur : reprendre une voiture et son carnet avec le code du vendeur et le matricule. */
export function TakeOver({ onDone }: { onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [plate, setPlate] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function check(e: React.FormEvent) {
    e.preventDefault();
    setMsg(""); setBusy(true);
    try { setPreview(await api<Preview>("/me/vehicle-transfers/preview", { method: "POST", json: { code, plate } })); }
    catch (err) { setMsg(errMsg(err)); }
    setBusy(false);
  }
  async function accept() {
    setBusy(true);
    try {
      await api("/me/vehicle-transfers/accept", { method: "POST", json: { code, plate } });
      setOpen(false); setPreview(null); setCode(""); setPlate("");
      onDone();
    } catch (err) { setMsg(errMsg(err)); }
    setBusy(false);
  }

  if (!open) return <button type="button" className="btn btn-ghost" onClick={() => setOpen(true)}>{t("transfer.takeOver")}</button>;
  return (
    <form className="car-form" onSubmit={check} noValidate>
      <h3>{t("transfer.takeOver")}</h3>
      <p className="help" style={{ marginTop: 0 }}>{t("transfer.takeOverHelp")}</p>
      <div className="row">
        <div>
          <label htmlFor="tr-code">{t("transfer.code")}</label>
          <input id="tr-code" autoCapitalize="characters" maxLength={12} value={code} placeholder="ABCD-2345"
            onChange={(e) => { setCode(e.target.value.toUpperCase()); setPreview(null); }} />
        </div>
        <div>
          <label htmlFor="tr-plate">{t("transfer.plate")}</label>
          <input id="tr-plate" inputMode="numeric" maxLength={24} value={plate} placeholder="12345-115-31"
            onChange={(e) => { setPlate(e.target.value); setPreview(null); }} />
        </div>
      </div>
      {preview && (
        <div className="notice transfer-preview" role="status">
          <strong>{preview.vehicle}</strong>
          <span>{t("transfer.previewLine", { visits: preview.visits, ct: preview.controles })}
            {preview.mileage_km != null ? ` · ${preview.mileage_km.toLocaleString("fr-FR")} km` : ""}</span>
          <span className="meta">{t(preview.include_prices ? "transfer.previewPrices" : "transfer.previewNoPrices")}</span>
        </div>
      )}
      {msg && <p className="err" role="alert">{msg}</p>}
      <div className="actions">
        {preview
          ? <button type="button" className="btn btn-primary" disabled={busy} onClick={accept}>{t("transfer.accept")}</button>
          : <button className="btn" disabled={busy || code.length < 8 || plate.length < 8}>{t("transfer.check")}</button>}
        <button type="button" className="btn btn-ghost" onClick={() => { setOpen(false); setPreview(null); }}>{t("account.cars.cancel")}</button>
      </div>
    </form>
  );
}
