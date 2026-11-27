"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import VoiceInput from "@/components/VoiceInput";
import { api, ApiError, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function Home() {
  const router = useRouter();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [text, setText] = useState("");
  const [dtc, setDtc] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [slow, setSlow] = useState(false);
  const onVoice = useCallback((s: string) => setText(s), []);

  // Un diagnostic prend 3 à 8 s sur le portable : au-delà de 3 s, on dit à l'utilisateur que ça avance.
  useEffect(() => {
    if (!busy) return setSlow(false);
    const timer = setTimeout(() => setSlow(true), 3000);
    return () => clearTimeout(timer);
  }, [busy]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const codes = dtc.split(/[\s,;]+/).map((c) => c.trim()).filter(Boolean);
    if (!text.trim() && !codes.length) return setError(t("home.error.empty"));
    setBusy(true);
    setError("");
    try {
      const r = await api<{ session_id: number }>("/diagnosis", {
        method: "POST",
        json: { text, dtc_codes: codes, variant_id: vehicle?.variantId ?? null, defer_llm: true },
      });
      router.push(`/diagnostic/${r.session_id}`);
    } catch (err) {
      setError(err instanceof ApiError && err.message ? err.message : t("common.error"));
      setBusy(false);
    }
  }

  return (
    <form className="hero" onSubmit={submit} noValidate>
      <h1>{t("home.title")}</h1>
      <p className="lead">{t("home.lead")}</p>

      <VehiclePicker onChange={setVehicle} />

      <label htmlFor="symptom">{t("home.label")}</label>
      <textarea
        id="symptom"
        name="symptom"
        placeholder={t("home.placeholder")}
        value={text}
        maxLength={2000}
        onChange={(e) => setText(e.target.value)}
      />
      <p className="help">{t("home.tip")}</p>
      {!text.trim() && (
        <div className="examples">
          <span className="help">{t("home.examples")}</span>
          <div className="chips">
            {[1, 2, 3].map((n) => (
              <button key={n} type="button" className="chip" onClick={() => setText(t(`home.example.${n}`))}>
                {t(`home.example.${n}`)}
              </button>
            ))}
          </div>
        </div>
      )}
      <VoiceInput onText={onVoice} />

      <label htmlFor="dtc">{t("home.dtc")}</label>
      <input
        id="dtc"
        name="dtc"
        placeholder={t("home.dtc.placeholder")}
        autoCapitalize="characters"
        value={dtc}
        onChange={(e) => setDtc(e.target.value.toUpperCase())}
        style={{ maxWidth: "14rem" }}
      />
      <p className="help">{t("home.dtc.help")}</p>

      {error && <p className="err" role="alert">{error}</p>}
      <div className="actions">
        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? t("home.submitting") : t("home.submit")}
        </button>
      </div>
      {busy && slow && <p className="help" role="status">{t("home.slow")}</p>}

      <div className="aside-link">
        <p style={{ marginBottom: "0.25rem" }}>{t("home.mechanic")}</p>
        <Link href="/pieces">{t("home.mechanic.link")}</Link>
      </div>
    </form>
  );
}
