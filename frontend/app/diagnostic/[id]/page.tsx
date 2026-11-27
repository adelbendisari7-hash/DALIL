"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, ApiError, lastDiagnosis } from "@/lib/api";
import { t } from "@/lib/i18n";

type Part = { category_id: number; slug: string; name: string };
type Ref = { oem_ref: string; part_brand: string | null; level: number; source: string };
type Cause = {
  fault: string; name: string; severity: string; description: string; confidence: number;
  part: Part; other_parts: Part[]; reference_level: number; references: Ref[]; explanation: string | null;
};
type Question = { id: string; text: string; options: string[] };
type Result = {
  session_id: number; status: "ok" | "clarify" | "unknown"; vehicle: string; variant_id?: number | null;
  causes: Cause[]; questions: Question[]; message: string | null; urgency?: string;
  dtc: { code: string; known: boolean; title_fr: string }[]; dtc_parts: (Part & { weight: number })[];
  safety: { do_not_drive: boolean; message: string | null }; disclaimer: string;
  // pending : résultat provisoire du classifieur, le modèle de langage affine en arrière-plan
  llm?: "off" | "pending" | "used" | "cached" | "fallback";
  // Texte en darija ou en arabe : ce que DALIL en a compris, en français, pour que l'utilisateur vérifie
  understood?: string | null;
};

function shopsHref(r: Result, p: Part) {
  const q = new URLSearchParams({ category: String(p.category_id), part: p.name, session: String(r.session_id) });
  if (r.variant_id) q.set("variant", String(r.variant_id));
  return `/magasins?${q}`;
}

function PartLabel({ cause, href }: { cause: Cause; href: string }) {
  const ref = cause.references[0];
  return (
    <div className="part-label">
      <span className="kind">{t("result.part")}</span>
      <span className="name">{cause.part.name}</span>
      {cause.reference_level >= 2 && ref ? (
        <span className="ref-level">
          {t(`result.ref.${cause.reference_level}`)} : <span className="ref">{ref.oem_ref}</span>
          {ref.part_brand ? ` (${ref.part_brand})` : ""}
        </span>
      ) : (
        <span className="ref-level">{t("result.ref.1")}</span>
      )}
      <div style={{ marginTop: "0.6rem" }}>
        <Link className="btn" href={href}>{t("result.findShops")}</Link>
      </div>
    </div>
  );
}

/** Résumé à envoyer au mécanicien : véhicule, première cause, pièce et lien du diagnostic. Aucune donnée personnelle. */
function ShareButton({ r }: { r: Result }) {
  const [copied, setCopied] = useState(false);
  const c = r.causes[0];
  if (!c) return null;
  async function share() {
    const text = t("result.share.text", {
      vehicle: r.vehicle, cause: c.name, part: c.part.name, confidence: Math.round(c.confidence * 100),
    });
    const url = window.location.href;
    if (navigator.share) {
      await navigator.share({ title: "DALIL", text, url }).catch(() => undefined);
      return;
    }
    try {
      await navigator.clipboard.writeText(`${text} ${url}`);
      setCopied(true);
    } catch {
      window.open(`https://wa.me/?text=${encodeURIComponent(`${text} ${url}`)}`, "_blank", "noopener");
    }
  }
  return (
    <div className="actions">
      <button type="button" className="btn btn-ghost" onClick={share}>{t("result.share")}</button>
      {copied && <span className="ok" role="status">{t("result.share.copied")}</span>}
    </div>
  );
}

type Family = { id: number; name: string; children: { id: number; name: string }[] };

/** « Ce diagnostic était-il juste ? ». Oui : la première pièce proposée est confirmée. Non : quelle pièce était en
 * cause ? Chaque réponse devient un vrai exemple candidat pour l'entraînement (python -m app.export_retours). */
function DiagnosisFeedback({ r }: { r: Result }) {
  const [step, setStep] = useState<"ask" | "which" | "done">("ask");
  const [families, setFamilies] = useState<Family[] | null>(null);
  const [other, setOther] = useState(false);
  const [picked, setPicked] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  // Pièces déjà proposées par DALIL, sauf la première (jugée fausse) : un toucher suffit dans la plupart des cas.
  const quick = [...r.causes.slice(1).map((c) => c.part), ...r.causes.flatMap((c) => c.other_parts)]
    .filter((p, i, all) => p.category_id !== r.causes[0]?.part.category_id && all.findIndex((q) => q.category_id === p.category_id) === i)
    .slice(0, 5);

  async function send(json: Record<string, unknown>) {
    setBusy(true);
    await api("/feedback", { method: "POST", json: { session_id: r.session_id, ...json } }).catch(() => undefined);
    setBusy(false);
    setStep("done");
  }
  function chooseOther() {
    setOther(true);
    if (!families) api<Family[]>("/parts/categories").then(setFamilies).catch(() => setFamilies([]));
  }

  if (step === "done") return <div className="feedback"><span className="ok" role="status">{t("result.feedback.thanks")}</span></div>;
  return (
    <div className="feedback">
      <p>{t("result.feedback.q")}</p>
      {step === "ask" ? (
        <div className="actions" style={{ marginTop: 0 }}>
          <button className="btn btn-ghost" disabled={busy}
            onClick={() => send({ diagnosis_correct: true, category_id: r.causes[0]?.part.category_id ?? null })}>
            {t("result.feedback.yes")}
          </button>
          <button className="btn btn-ghost" onClick={() => setStep("which")}>{t("result.feedback.no")}</button>
        </div>
      ) : (
        <div className="questions">
          <p className="help" style={{ marginTop: 0 }}>{t("result.feedback.which")}</p>
          <div className="chips">
            {quick.map((p) => (
              <button key={p.category_id} type="button" className="chip" aria-pressed={picked === p.category_id}
                onClick={() => { setPicked(p.category_id); setOther(false); }}>{p.name}</button>
            ))}
            <button type="button" className="chip" aria-pressed={other} onClick={chooseOther}>{t("result.feedback.other")}</button>
          </div>
          {other && (
            <>
              <label htmlFor="fb-part">{t("result.feedback.choose")}</label>
              <select id="fb-part" value={picked ?? ""} onChange={(e) => setPicked(e.target.value ? Number(e.target.value) : null)}>
                <option value="">—</option>
                {(families ?? []).map((f) => (
                  <optgroup key={f.id} label={f.name}>
                    {f.children.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </optgroup>
                ))}
              </select>
            </>
          )}
          <label htmlFor="fb-comment">{t("result.feedback.comment")}</label>
          <input id="fb-comment" maxLength={300} value={comment} placeholder={t("result.feedback.comment.placeholder")}
            onChange={(e) => setComment(e.target.value)} />
          <div className="actions">
            <button className="btn" disabled={busy || picked === null}
              onClick={() => send({ diagnosis_correct: false, category_id: picked, comment: comment.trim() || null })}>
              {t("result.feedback.send")}
            </button>
            <button className="btn btn-ghost" disabled={busy}
              onClick={() => send({ diagnosis_correct: false, comment: comment.trim() || null })}>
              {t("result.feedback.unknown")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DiagnosticResult() {
  const { id } = useParams<{ id: string }>();
  const [r, setR] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  // Sans réseau : le dernier diagnostic gardé sur l'appareil, avec sa date
  const [offline, setOffline] = useState<string | null>(null);

  useEffect(() => {
    api<Result>(`/diagnosis/${id}`).then((res) => { setR(res); setOffline(null); })
      .catch((e) => {
        const saved = lastDiagnosis.get();
        if (e instanceof ApiError && e.status === 0 && saved && saved.id === Number(id)) {
          setR(saved.result as Result);
          setOffline(saved.savedAt);
          return;
        }
        setError(e instanceof ApiError && e.status === 404 ? t("diagnosis.notFound")
          : e instanceof ApiError && e.status === 0 ? t("offline.none") : t("common.error"));
      });
  }, [id]);

  // Chaque résultat définitif est gardé sur l'appareil (consultable hors ligne)
  useEffect(() => {
    if (r && !offline && r.llm !== "pending") lastDiagnosis.saveResult(r.session_id, r);
  }, [r, offline]);

  // Tant que le modèle de langage travaille (20 à 45 s sur le portable), on garde le résultat provisoire à l'écran
  // et on relit le résultat toutes les 2,5 s ; il remplace le provisoire dès que `llm` n'est plus « pending ».
  useEffect(() => {
    if (r?.llm !== "pending") return;
    const timer = setInterval(() => {
      api<Result>(`/diagnosis/${id}`).then((next) => { if (next.llm !== "pending") setR(next); }).catch(() => undefined);
    }, 2500);
    return () => clearInterval(timer);
  }, [r?.llm, id]);

  async function answer(qid: string, idx: number) {
    if (!r) return;
    setBusy(true);
    try {
      const next = await api<Result>(`/diagnosis/${r.session_id}/answers`, { method: "POST", json: { answers: { [qid]: idx }, defer_llm: true } });
      setR({ ...next, variant_id: r.variant_id });
    } catch (e) {
      setError(e instanceof ApiError && e.message ? e.message : t("common.error"));
    }
    setBusy(false);
  }

  if (error) return <p className="err" role="alert">{error}</p>;
  if (!r) return <p>{t("common.loading")}</p>;

  return (
    <article>
      {offline && (
        <p className="notice offline-note" role="status">
          {t("offline.result", { date: new Date(offline).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" }) })}
        </p>
      )}
      <span className="vehicle-pill">{t("result.for")} {r.vehicle}</span>
      {r.understood && <p className="notice" role="status">{t("result.understood")} « {r.understood} »</p>}
      {r.llm === "pending" && <p className="notice" role="status">{t("result.refining")}</p>}
      {r.safety.do_not_drive && <div className="danger" role="alert">{r.safety.message}</div>}

      {r.dtc.length > 0 && (
        <section>
          <h2>{t("result.dtc.title")}</h2>
          <ul className="list">
            {r.dtc.map((d) => (
              <li key={d.code}><span><strong>{d.code}</strong> {d.title_fr}</span></li>
            ))}
          </ul>
        </section>
      )}

      {r.status === "unknown" ? (
        <section>
          <h1>{t("result.unknown.title")}</h1>
          <p>{r.message}</p>
          {r.dtc_parts.length > 0 && (
            <>
              <h3>{t("result.dtc.parts")}</h3>
              <ul className="list">
                {r.dtc_parts.map((p) => (
                  <li key={p.category_id}>
                    <span>{p.name}</span>
                    <Link href={shopsHref(r, p)}>{t("result.findShops")}</Link>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      ) : (
        <section>
          <h1>{t("result.title")}</h1>
          {r.status === "clarify" && r.questions.length > 0 && (
            <div className="questions" aria-busy={busy}>
              <h3>{t("result.questions")}</h3>
              {r.questions.map((q) => (
                <div className="question" key={q.id}>
                  <p>{q.text}</p>
                  <div className="chips">
                    {q.options.map((o, i) => (
                      <button key={o} type="button" className="chip" disabled={busy} onClick={() => answer(q.id, i)}>{o}</button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
          <ol className="causes">
            {r.causes.map((c, i) => (
              <li className="cause" key={c.fault}>
                {i === 0 && r.causes.length > 1 && <span className="cause-badge">{t("result.best")}</span>}
                <div className="cause-head">
                  <h3>{c.name}</h3>
                  <span className="cause-rank" data-sev={c.severity}>{t(`result.urgency.${c.severity}`)}</span>
                </div>
                {/* jauge animée par transform (compositeur) : la largeur est l'échelle horizontale */}
                <div className="meter" aria-hidden>
                  <span style={{ transform: `scaleX(${Math.max(0.02, c.confidence)})` }} />
                </div>
                <span className="meta">{t("result.confidence")} {Math.round(c.confidence * 100)} %</span>
                <p>{c.explanation || c.description}</p>
                {i === 0 ? (
                  <PartLabel cause={c} href={shopsHref(r, c.part)} />
                ) : (
                  <p>
                    {t("result.part")} : <Link href={shopsHref(r, c.part)}>{c.part.name}</Link>
                  </p>
                )}
                {c.other_parts.length > 0 && (
                  <p className="meta">
                    {t("result.also")} :{" "}
                    {c.other_parts.map((p, j) => (
                      <span key={p.slug}>{j > 0 && ", "}<Link href={shopsHref(r, p)}>{p.name.toLowerCase()}</Link></span>
                    ))}
                  </p>
                )}
              </li>
            ))}
          </ol>
          <div className="card">
            <DiagnosisFeedback r={r} />
            <ShareButton r={r} />
          </div>
        </section>
      )}

      <div className="notice">{r.disclaimer}</div>
      <p className="result-foot"><Link className="btn btn-ghost" href="/">{t("result.newSearch")}</Link></p>
    </article>
  );
}
