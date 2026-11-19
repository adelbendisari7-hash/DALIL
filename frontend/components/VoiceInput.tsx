"use client";
import { useEffect, useRef, useState } from "react";
import { t } from "@/lib/i18n";

/* Saisie vocale (F13), première version : reconnaissance du navigateur en fr-FR.
   La transcription arrive dans la zone de texte, où l'utilisateur la corrige avant d'envoyer.
   Version suivante prévue : enregistrement envoyé à Whisper côté serveur (section 6.5). */
type Rec = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: (e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void;
  onend: () => void;
  onerror: (e: { error?: string }) => void;
  start: () => void;
  stop: () => void;
};

export default function VoiceInput({ onText }: { onText: (text: string) => void }) {
  const [supported, setSupported] = useState(true);
  const [listening, setListening] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [secure, setSecure] = useState(true);
  const rec = useRef<Rec | null>(null);

  useEffect(() => {
    const w = window as unknown as { SpeechRecognition?: new () => Rec; webkitSpeechRecognition?: new () => Rec };
    const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!Ctor) {
      setSupported(false);
      return;
    }
    // Le micro n'est accordé que sur https ou localhost : sur l'adresse du PC (http://192.168…), Chrome le refuse.
    if (!window.isSecureContext) {
      setSecure(false);
      return;
    }
    const r = new Ctor();
    r.lang = "fr-FR";
    r.interimResults = true;
    r.continuous = false;
    r.onresult = (e) => onText(Array.from(e.results).map((res) => res[0].transcript).join(" "));
    r.onend = () => {
      setListening(false);
      setDone(true);
    };
    r.onerror = (e) => {
      setListening(false);
      const code = e?.error || "";
      setError(code === "not-allowed" || code === "service-not-allowed" ? t("voice.error.denied")
        : code === "no-speech" ? t("voice.error.nospeech")
        : code === "network" ? t("voice.error.network")
        : code === "aborted" ? "" : t("voice.error.other"));
    };
    rec.current = r;
  }, [onText]);

  if (!supported) return <p className="help">{t("voice.unsupported")}</p>;
  if (!secure) return <p className="help">{t("voice.insecure")}</p>;
  return (
    <div className="voice">
      <button
        type="button"
        className="btn btn-ghost"
        aria-pressed={listening}
        onClick={() => {
          if (listening) rec.current?.stop();
          else {
            setDone(false);
            setError("");
            try {
              rec.current?.start();
              setListening(true);
            } catch {
              setError(t("voice.error.other"));
            }
          }
        }}
      >
        {listening ? t("voice.stop") : t("voice.start")}
      </button>
      {listening && (
        <>
          <span className="rec" aria-hidden />
          <span className="status" role="status">{t("voice.listening")}</span>
        </>
      )}
      {done && !listening && !error && <span className="status" role="status">{t("voice.review")}</span>}
      {error && <span className="status" role="alert">{error}</span>}
    </div>
  );
}
