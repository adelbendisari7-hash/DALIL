"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import { paperWhen } from "@/components/Papers";
import { shopsLink, watchLine, type Watch } from "@/components/PriceWatches";
import { recallsSeen } from "@/components/Recalls";
import VoiceInput from "@/components/VoiceInput";
import WarningLights, { lightPhrase, type Light } from "@/components/WarningLights";
import { api, ApiError, lastDiagnosis, session, store, type LastDiagnosis, type UserCar, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

type Due = NonNullable<UserCar["maintenance_items"]>[number];
function upkeepWhen(x: Due): string {
  if (x.status === "due") {
    if (x.km_left != null && x.km_left <= 0) return t("upkeep.overKm", { km: Math.abs(x.km_left).toLocaleString("fr-FR") });
    return t("upkeep.due");
  }
  if (x.km_left != null && x.km_left <= 1500) return t("upkeep.inKm", { km: x.km_left.toLocaleString("fr-FR") });
  if (x.days_left != null) return t("upkeep.inDays", { n: x.days_left });
  return t("upkeep.soon");
}

function lastSummary(l: LastDiagnosis): string {
  const r = l.result as { vehicle?: string; causes?: { name: string }[] };
  const cause = r.causes?.[0]?.name;
  return [cause ?? t("offline.last.unknown"), r.vehicle].filter(Boolean).join(" · ");
}

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
  // Dernier diagnostic gardé sur l'appareil (relisible sans réseau)
  const [last, setLast] = useState<LastDiagnosis | null>(null);
  // Rappel d'entretien masqué pour aujourd'hui
  const [upkeepHidden, setUpkeepHidden] = useState(true);
  useEffect(() => {
    setLast(lastDiagnosis.get());
    setUpkeepHidden(store.read("dalil.upkeep.hidden") === new Date().toDateString());
  }, []);
  function hideUpkeep() {
    store.write("dalil.upkeep.hidden", new Date().toDateString());
    setUpkeepHidden(true);
  }
  const upkeep = cars.filter((c) => c.maintenance_items?.length);
  // Rappels possibles pas encore regardés (le panneau « Rappels » de la voiture les marque comme vus)
  const [seenRecalls, setSeenRecalls] = useState<Record<string, number>>({});
  useEffect(() => { setSeenRecalls(recallsSeen.get()); }, []);
  const recallCars = cars.filter((c) => (c.recalls_count ?? 0) > (seenRecalls[c.id] ?? 0));
  // Pièces suivies dont le prix a baissé, ou qu'un magasin propose enfin
  const [watchAlerts, setWatchAlerts] = useState<Watch[]>([]);
  useEffect(() => {
    if (!session.token()) return;
    api<Watch[]>("/me/price-watches").then((ws) => setWatchAlerts(ws.filter((w) => w.alert))).catch(() => undefined);
  }, []);
  // Papiers qui finissent bientôt : « bientôt » se masque pour la journée, urgent (7 jours) ou expiré reste affiché
  const [papersHidden, setPapersHidden] = useState(true);
  useEffect(() => { setPapersHidden(store.read("dalil.papers.hidden") === new Date().toDateString()); }, []);
  const paperAlerts = cars.flatMap((c) => (c.papers_alerts ?? []).map((p) => ({ car: c, p })))
    .filter(({ p }) => !papersHidden || p.status !== "soon")
    .sort((a, b) => a.p.days_left - b.p.days_left);
  const papersUrgent = paperAlerts.some(({ p }) => p.status !== "soon");
  function hidePapers() {
    store.write("dalil.papers.hidden", new Date().toDateString());
    setPapersHidden(true);
  }
  const [text, setText] = useState("");
  const [lights, setLights] = useState<string[]>([]);

  // Toucher un voyant ajoute (ou retire) sa description au texte : la chaîne de diagnostic habituelle s'en charge
  function toggleLight(l: Light) {
    const phrase = lightPhrase(l.id);
    if (lights.includes(l.id)) {
      setLights(lights.filter((x) => x !== l.id));
      setText((cur) => cur.split(", ").filter((x) => x !== phrase).join(", "));
    } else {
      setLights([...lights, l.id]);
      setText((cur) => (cur.trim() ? `${cur.trim()}, ${phrase}` : phrase));
    }
  }
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

      {/* Contrôle technique et assurance : rappel dès 30 jours avant la fin */}
      {paperAlerts.length > 0 && (
        <aside className={`card upkeep-banner papers-banner${papersUrgent ? " is-urgent" : ""}`} aria-labelledby="papers-title">
          <div className="upkeep-head">
            <h2 id="papers-title" className="card-title">{t("papers.banner")}</h2>
            {!papersUrgent && <button type="button" className="btn btn-ghost" onClick={hidePapers}>{t("upkeep.hide")}</button>}
          </div>
          <ul className="upkeep-list">
            {paperAlerts.map(({ car: c, p }) => (
              <li key={p.id}>
                <Link href={`/compte?papiers=${c.id}#voiture-${c.id}`}>
                  <strong>{t(`papers.${p.kind}`)} · {c.nickname || c.display}</strong>
                  <span className={`meta${p.status !== "soon" ? " paper-urgent" : ""}`}>{paperWhen(p)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </aside>
      )}

      {recallCars.length > 0 && (
        <aside className="card upkeep-banner recall-banner" aria-labelledby="recall-title">
          <h2 id="recall-title" className="card-title">{t("recalls.banner")}</h2>
          <ul className="upkeep-list">
            {recallCars.map((c) => (
              <li key={c.id}>
                <Link href={`/compte?rappels=${c.id}#voiture-${c.id}`}>
                  <strong>{c.nickname || c.display}</strong>
                  <span className="meta">{t("recalls.bannerLine", { n: c.recalls_count ?? 0 })}</span>
                </Link>
              </li>
            ))}
          </ul>
          <p className="help">{t("recalls.bannerHelp")}</p>
        </aside>
      )}

      {watchAlerts.length > 0 && (
        <aside className="card upkeep-banner price-banner" aria-labelledby="price-alert-title">
          <h2 id="price-alert-title" className="card-title">{t("watch.banner")}</h2>
          <ul className="upkeep-list">
            {watchAlerts.map((w) => (
              <li key={w.id}>
                <Link href={shopsLink(w)}>
                  <strong>{w.part}</strong>
                  <span className="meta">{watchLine(w)}</span>
                </Link>
              </li>
            ))}
          </ul>
          <p className="help">{t("watch.banner.help")}</p>
        </aside>
      )}

      {/* Rappel d'entretien : seulement ce qui est dépassé ou proche, masquable pour la journée */}
      {!upkeepHidden && upkeep.length > 0 && (
        <aside className="card upkeep-banner" aria-labelledby="upkeep-title">
          <div className="upkeep-head">
            <h2 id="upkeep-title" className="card-title">{t("upkeep.title")}</h2>
            <button type="button" className="btn btn-ghost" onClick={hideUpkeep}>{t("upkeep.hide")}</button>
          </div>
          <ul className="upkeep-list">
            {upkeep.map((c) => (
              <li key={c.id}>
                <Link href={`/compte?entretien=${c.id}#voiture-${c.id}`}>
                  <strong>{c.nickname || c.display}</strong>
                  <span className="meta">
                    {c.maintenance_items!.slice(0, 3).map((x) => `${x.name.toLowerCase()} (${upkeepWhen(x)})`).join(", ")}
                    {c.maintenance_items!.length > 3 ? ` +${c.maintenance_items!.length - 3}` : ""}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <p className="help">{t("upkeep.note")}</p>
        </aside>
      )}

      {last && (
        <Link className="card last-diagnosis" href={`/diagnostic/${last.id}`}>
          <span className="card-title">{t("offline.last")}</span>
          <span>{lastSummary(last)}</span>
          <span className="meta">{t("offline.last.help", { date: new Date(last.savedAt).toLocaleDateString("fr-FR") })}</span>
        </Link>
      )}

      {/* 1. Le problème : la tâche principale vient en premier */}
      <div className="card">
        <label htmlFor="symptom" className="card-title">{t("home.label")}</label>
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
      </div>

      {/* Un voyant allumé : le toucher suffit, pour qui ne sait pas le décrire */}
      <div className="card">
        <h2 className="card-title">{t("lights.title")}</h2>
        <p className="help" style={{ marginTop: 0 }}>{t("lights.help")}</p>
        <WarningLights selected={lights} onToggle={toggleLight} />
      </div>

      {/* 2. Le véhicule : une voiture du compte en un toucher, sinon le sélecteur */}
      <div className="card">
        {cars.length > 0 && (
          <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
            <legend className="card-title">{t("home.car")}</legend>
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
        {car === "other" && <div style={cars.length ? { marginTop: "1rem" } : undefined}><VehiclePicker onChange={setVehicle} /></div>}
      </div>

      {/* 3. Le code défaut, pour qui en a un */}
      <div className="card">
        <label htmlFor="dtc" className="card-title">{t("home.dtc")}</label>
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
      </div>

      {error && <p className="err" role="alert">{error}</p>}
      <div className="submit-zone">
        <button className={`btn btn-primary btn-block${busy ? " is-busy" : ""}`} disabled={busy}>
          {busy ? t("home.submitting") : t("home.submit")}
        </button>
        {busy && slow && <p className="help" role="status" style={{ textAlign: "center" }}>{t("home.slow")}</p>}
      </div>

      <div className="aside-link">
        <p>{t("home.mechanic")}</p>
        <Link href="/pieces">{t("home.mechanic.link")}</Link>
      </div>
    </form>
  );
}
