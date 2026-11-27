"use client";
import { useEffect, useState } from "react";
import { api, store, type UserCar } from "@/lib/api";
import { t } from "@/lib/i18n";

type Recall = { id: number; models: string; motif: string; risque: string | null; date: string | null; url: string | null;
  match: "generation" | "model" };

/** Rappels vus pour chaque voiture (nombre), pour ne plus les signaler sur l'accueil. */
export const recallsSeen = {
  get: (): Record<string, number> => { try { return JSON.parse(store.read("dalil.recalls.seen") || "{}"); } catch { return {}; } },
  set: (carId: number, n: number) => store.write("dalil.recalls.seen", JSON.stringify({ ...recallsSeen.get(), [carId]: n })),
};

const day = (iso: string) => new Date(iso).toLocaleDateString("fr-FR");

/** Rappels publiés en France pour le modèle de la voiture : « rappel possible », jamais « concernée ». */
export default function Recalls({ car }: { car: UserCar }) {
  const [data, setData] = useState<{ recalls: Recall[]; vin: string | null; source: string } | null>(null);
  useEffect(() => {
    api<{ recalls: Recall[]; vin: string | null; source: string }>(`/me/vehicles/${car.id}/recalls`)
      .then((d) => { setData(d); recallsSeen.set(car.id, d.recalls.length); })
      .catch(() => setData({ recalls: [], vin: null, source: "" }));
  }, [car.id]);

  if (!data) return <p>{t("common.loading")}</p>;
  return (
    <div className="maintenance recalls">
      <p className="notice" style={{ marginTop: 0 }}>{t("recalls.warning")}</p>
      {data.recalls.length === 0 ? <p className="help">{t("recalls.none")}</p> : (
        <ol className="carnet-list">
          {data.recalls.map((r) => (
            <li key={r.id} className="visit recall">
              <div className="status-head">
                <strong>{r.date ? day(r.date) : t("recalls.noDate")}</strong>
                <span className={`maint-pill ${r.match === "generation" ? "is-check" : ""}`}>
                  {t(r.match === "generation" ? "recalls.match.generation" : "recalls.match.model")}
                </span>
              </div>
              <span className="meta">{t("recalls.models", { models: r.models })}</span>
              <span>{r.motif}</span>
              {r.risque && <span className="meta">{t("recalls.risk", { risk: r.risque })}</span>}
              {r.url && (
                <a href={r.url} target="_blank" rel="noopener noreferrer" className="recall-link">{t("recalls.official")}</a>
              )}
            </li>
          ))}
        </ol>
      )}
      <p className="help">{data.vin ? t("recalls.vin", { vin: data.vin }) : t("recalls.noVin")}</p>
      {data.source && <p className="help">{t("recalls.source", { source: data.source })}</p>}
    </div>
  );
}
