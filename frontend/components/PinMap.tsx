"use client";
import { useEffect, useRef, useState } from "react";
import type * as L from "leaflet";
import "leaflet/dist/leaflet.css";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export type Pin = { lat: number; lng: number };
type Hit = { label: string; lat: number; lng: number };

const ORAN: [number, number] = [35.6971, -0.6308];
const round = (x: number) => +x.toFixed(6);

/** Position du magasin : adresse tapée (lieux de la wilaya d'Oran), ou « je suis au magasin » ; dans les deux cas
 * l'épingle se déplace au doigt (les adresses d'Oran sont souvent approximatives) ou d'un toucher sur la carte. */
export default function PinMap({ value, onChange, address, onAddress }: {
  value: Pin | null; onChange: (p: Pin) => void; address: string; onAddress: (a: string) => void;
}) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const marker = useRef<L.Marker | null>(null);
  const lib = useRef<typeof L | null>(null);
  const [hits, setHits] = useState<Hit[]>([]);
  const [searching, setSearching] = useState(false);
  const [msg, setMsg] = useState("");
  const typed = useRef(false);   // la recherche ne part que si l'adresse a été tapée (pas au chargement de la fiche)

  // Carte et épingle
  useEffect(() => {
    let cancelled = false;
    import("leaflet").then((Lf) => {
      if (cancelled || !el.current || map.current) return;
      lib.current = Lf;
      const m = Lf.map(el.current).setView(value ? [value.lat, value.lng] : ORAN, value ? 17 : 12);
      Lf.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© contributeurs OpenStreetMap" }).addTo(m);
      m.on("click", (e: L.LeafletMouseEvent) => onChange({ lat: round(e.latlng.lat), lng: round(e.latlng.lng) }));
      map.current = m;
      if (value) place(value, false);
    });
    return () => {
      cancelled = true;
      map.current?.remove();
      map.current = null;
      marker.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function place(p: Pin, fly: boolean) {
    const Lf = lib.current;
    const m = map.current;
    if (!Lf || !m) return;
    if (!marker.current) {
      const icon = Lf.divIcon({
        className: "",
        html: '<div class="pin"><span></span></div>',
        iconSize: [34, 44],
        iconAnchor: [17, 42],
      });
      marker.current = Lf.marker([p.lat, p.lng], { draggable: true, icon, autoPan: true, keyboard: true, title: t("shop.pin.drag") }).addTo(m);
      marker.current.on("dragend", () => {
        const ll = marker.current!.getLatLng();
        onChange({ lat: round(ll.lat), lng: round(ll.lng) });
      });
    } else {
      marker.current.setLatLng([p.lat, p.lng]);
    }
    if (fly) m.flyTo([p.lat, p.lng], Math.max(m.getZoom(), 17), { duration: 0.6 });
  }

  // L'épingle suit la valeur (recherche, position du téléphone, toucher sur la carte)
  useEffect(() => { if (value) place(value, true); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [value?.lat, value?.lng]);

  // Recherche d'adresse : une requête après 700 ms sans frappe (le service limite à une par seconde)
  useEffect(() => {
    if (!typed.current || address.trim().length < 4) return setHits([]);
    const id = setTimeout(() => {
      setSearching(true);
      api<Hit[]>(`/geo/geocode?q=${encodeURIComponent(address.trim())}`)
        .then((h) => { setHits(h); setMsg(h.length ? "" : t("shop.address.notFound")); })
        .catch(() => setHits([]))
        .finally(() => setSearching(false));
    }, 700);
    return () => clearTimeout(id);
  }, [address]);

  function here() {
    if (!navigator.geolocation) return setMsg(t("shops.locate.denied"));
    setMsg(t("shops.locating"));
    navigator.geolocation.getCurrentPosition(
      (p) => { onChange({ lat: round(p.coords.latitude), lng: round(p.coords.longitude) }); setMsg(t("shop.position.ok")); },
      () => setMsg(t("shops.locate.denied")),
      { enableHighAccuracy: true, timeout: 15000 },
    );
  }

  return (
    <div className="pinmap">
      <label htmlFor="s-addr">{t("shops.address")}</label>
      <input id="s-addr" autoComplete="street-address" placeholder={t("shop.address.placeholder")} value={address}
        onChange={(e) => { typed.current = true; onAddress(e.target.value); }} />
      {searching && <p className="help" role="status">{t("shop.address.searching")}</p>}
      {hits.length > 0 && (
        <ul className="suggestions" role="listbox" aria-label={t("shop.address.suggestions")}>
          {hits.map((h) => (
            <li key={`${h.lat},${h.lng}`}>
              <button type="button" role="option" aria-selected={false}
                onClick={() => { onChange({ lat: h.lat, lng: h.lng }); setHits([]); setMsg(t("shop.pin.adjust")); }}>
                {h.label}
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="actions" style={{ marginTop: "0.6rem" }}>
        <button type="button" className="btn btn-ghost" onClick={here}>{t("shop.position.here")}</button>
      </div>
      <div ref={el} className="map pin-map" aria-label={t("shop.pin.map")} />
      <p className="help" role="status">{msg || (value ? t("shop.pin.adjust") : t("shop.pin.none"))}</p>
    </div>
  );
}
