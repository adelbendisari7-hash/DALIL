"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
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

export default function DiagnosticResult() {
  const { id } = useParams<{ id: string }>();
  const [r, setR] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState(false);

  useEffect(() => {
    api<Result>(`/diagnosis/${id}`).then(setR)
      .catch((e) => setError(e instanceof ApiError && e.status === 404 ? t("diagnosis.notFound") : t("common.error")));
  }, [id]);

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

  async function rate(ok: boolean) {
    await api("/feedback", { method: "POST", json: { session_id: r?.session_id, diagnosis_correct: ok } }).catch(() => undefined);
    setFeedback(true);
  }

  if (error) return <p className="err" role="alert">{error}</p>;
  if (!r) return <p>{t("common.loading")}</p>;

  return (
    <article>
      <p className="meta">{t("result.for")} {r.vehicle}</p>
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
                <div className="cause-head">
                  <h3>{c.name}</h3>
                  <span className="cause-rank">{t(`result.urgency.${c.severity}`)}</span>
                </div>
                <div className="meter" aria-hidden><span style={{ width: `${Math.round(c.confidence * 100)}%` }} /></div>
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
          <div className="feedback">
            <p>{t("result.feedback.q")}</p>
            <div className="actions" style={{ marginTop: 0 }}>
            {feedback ? (
              <span className="ok">{t("result.feedback.thanks")}</span>
            ) : (
              <>
                <button className="btn btn-ghost" onClick={() => rate(true)}>{t("result.feedback.yes")}</button>
                <button className="btn btn-ghost" onClick={() => rate(false)}>{t("result.feedback.no")}</button>
              </>
            )}
            </div>
          </div>
        </section>
      )}

      <div className="notice">{r.disclaimer}</div>
      <Link href="/">{t("result.newSearch")}</Link>
    </article>
  );
}
