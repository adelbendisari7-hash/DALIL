"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import VehiclePicker from "@/components/VehiclePicker";
import { api, type Vehicle } from "@/lib/api";
import { t } from "@/lib/i18n";

type Hit = { id: number; slug: string; name: string; parent_id: number | null };
type Family = { id: number; name: string; children: { id: number; name: string }[] };
type RefHit = { oem_ref: string; category_id: number; vehicle?: string; title?: string; level: number };

/** Parcours direct du mécanicien : pièce + véhicule -> magasins. */
export default function PartsPage() {
  const router = useRouter();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [families, setFamilies] = useState<Family[]>([]);
  const [ref, setRef] = useState("");
  const [refHits, setRefHits] = useState<RefHit[] | null>(null);

  useEffect(() => {
    api<Family[]>("/parts/categories").then(setFamilies).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (q.trim().length < 2) return setHits([]);
    const h = setTimeout(() => {
      api<Hit[]>(`/parts/search?q=${encodeURIComponent(q.trim())}`).then(setHits).catch(() => setHits([]));
    }, 200);
    return () => clearTimeout(h);
  }, [q]);

  function go(categoryId: number, name: string) {
    const p = new URLSearchParams({ category: String(categoryId), part: name });
    if (vehicle) p.set("variant", String(vehicle.variantId));
    router.push(`/magasins?${p}`);
  }

  async function searchRef(e: React.FormEvent) {
    e.preventDefault();
    if (ref.trim().length < 3) return;
    setRefHits(await api<RefHit[]>(`/parts/references?ref=${encodeURIComponent(ref.trim())}`).catch(() => []));
  }

  const nameOf = (id: number) => families.flatMap((f) => [f, ...f.children]).find((c) => c.id === id)?.name ?? "";

  return (
    <section>
      <h1>{t("parts.title")}</h1>
      <p className="lead">{t("parts.lead")}</p>
      <VehiclePicker onChange={setVehicle} />

      <label htmlFor="part-q">{t("parts.search")}</label>
      <input id="part-q" type="search" autoComplete="off" placeholder={t("parts.search.placeholder")} value={q} onChange={(e) => setQ(e.target.value)} />
      {q.trim().length >= 2 && (
        hits.length ? (
          <ul className="list" aria-live="polite">
            {hits.map((h) => (
              <li key={h.id}>
                <span>{h.name}</span>
                <button className="btn" onClick={() => go(h.id, h.name)}>{t("result.findShops")}</button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="help">{t("parts.noResult")}</p>
        )
      )}

      <form onSubmit={searchRef}>
        <label htmlFor="part-ref">{t("parts.ref")}</label>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <input id="part-ref" placeholder={t("parts.ref.placeholder")} value={ref} onChange={(e) => setRef(e.target.value)} />
          <button className="btn">{t("parts.ref.search")}</button>
        </div>
      </form>
      {refHits && (refHits.length ? (
        <ul className="list">
          {refHits.map((r, i) => (
            <li key={`${r.oem_ref}-${i}`}>
              <span><strong>{r.oem_ref}</strong> {r.title || nameOf(r.category_id)} {r.vehicle ? `(${r.vehicle})` : ""}</span>
              <button className="btn btn-ghost" onClick={() => go(r.category_id, nameOf(r.category_id))}>{t("result.findShops")}</button>
            </li>
          ))}
        </ul>
      ) : <p className="help">{t("parts.ref.none")}</p>)}

      <h2 className="section">{t("parts.browse")}</h2>
      {families.map((f) => (
        <details key={f.id}>
          <summary style={{ padding: "0.7rem 0", borderTop: "1px solid var(--line)", cursor: "pointer", fontWeight: 600 }}>{f.name}</summary>
          <div className="chips" style={{ paddingBottom: "0.8rem" }}>
            {f.children.map((c) => <button key={c.id} className="chip" onClick={() => go(c.id, c.name)}>{c.name}</button>)}
          </div>
        </details>
      ))}
    </section>
  );
}
