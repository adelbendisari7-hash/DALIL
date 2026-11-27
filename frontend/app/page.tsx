"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import VoiceInput from "@/components/VoiceInput";
import { api, ApiError, session, type UserCar, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function Home() {
  const router = useRouter();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  // Client connecté avec des voitures : il choisit l'une d'elles (le diagnostic est rangé dans son historique)
  const [cars, setCars] = useState<UserCar[]>([]);
  const [car, setCar] = useState<number | "other">("other");
  useEffect(() => {
    if (!session.token()) return;
    api<UserCar[]>("/me/vehicles")
      .then((cs) => { setCars(cs); if (cs.length) setCar(cs[0].id); })
      .catch(() => undefined);
  }, []);
  const [text, setText] = useState("");
  const [dtc, setDtc] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [slow, setSlow] = useState(false);
  const [warming, setWarming] = useState(false);
  const onVoice = useCallback((s: string) => setText(s), []);

  // Juste après le démarrage, l'API charge ses modèles (~30 s) : on le dit plutôt que de laisser croire à une panne.
  useEffect(() => {
    let stop = false;
    let timer: ReturnType<typeof setTimeout>;
    const check = () =>
      api<{ ready?: boolean }>("/health")
        .then((h) => {
          if (stop) return;
          setWarming(h.ready === false);
          if (h.ready === false) timer = setTimeout(check, 3000);
        })
        .catch(() => undefined);
    check();
    return () => { stop = true; clearTimeout(timer); };
  }, []);

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
        json: car !== "other"
          ? { text, dtc_codes: codes, user_vehicle_id: car, defer_llm: true }
          : { text, dtc_codes: codes, variant_id: vehicle?.variantId ?? null, defer_llm: true },
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
      {warming && <p className="notice" role="status">{t("home.warming")}</p>}

      {cars.length > 0 && (
        <fieldset style={{ border: 0, padding: 0, margin: "1.25rem 0 0" }}>
          <legend style={{ fontWeight: 600 }}>{t("home.car")}</legend>
          <div className="chips">
            {cars.map((c) => (
              <button key={c.id} type="button" className="chip" aria-pressed={car === c.id} onClick={() => setCar(c.id)}>
                {c.nickname || c.display}
              </button>
            ))}
            <button type="button" className="chip" aria-pressed={car === "other"} onClick={() => setCar("other")}>
              {t("home.car.other")}
            </button>
          </div>
        </fieldset>
      )}
      {car === "other" && <VehiclePicker onChange={setVehicle} />}

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
