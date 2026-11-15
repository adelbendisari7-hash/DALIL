"use client";
import { useEffect, useRef } from "react";
import type * as L from "leaflet";
import "leaflet/dist/leaflet.css";

export type MapShop = { id: number; name: string; lat: number | null; lng: number | null; reasons?: string[] };

const ORAN: [number, number] = [35.6971, -0.6308];

/** Carte Leaflet avec fond OpenStreetMap (gratuit, sans clé). Les marqueurs portent le rang de la liste. */
export default function ShopMap({ shops, me }: { shops: MapShop[]; me?: [number, number] | null }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);

  useEffect(() => {
    let cancelled = false;
    import("leaflet").then((Lf) => {
      if (cancelled || !el.current) return;
      if (!map.current) {
        map.current = Lf.map(el.current).setView(me ?? ORAN, 12);
        Lf.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution: "© contributeurs OpenStreetMap",
        }).addTo(map.current);
      }
      const m = map.current;
      m.eachLayer((layer) => {
        if (!(layer instanceof Lf.TileLayer)) m.removeLayer(layer);
      });
      const pts: [number, number][] = [];
      shops.forEach((s, i) => {
        if (s.lat == null || s.lng == null) return;
        pts.push([s.lat, s.lng]);
        const icon = Lf.divIcon({
          className: "",
          html: `<div style="background:#f2b705;color:#14202c;border:2px solid #152a42;border-radius:50%;width:28px;height:28px;display:grid;place-items:center;font-weight:800;font-family:sans-serif">${i + 1}</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        });
        const popup = document.createElement("div");
        const a = document.createElement("a");
        a.href = `/magasins/${s.id}`;
        a.textContent = s.name;
        popup.appendChild(a);
        if (s.reasons?.length) {
          const p = document.createElement("div");
          p.textContent = s.reasons.join(", ");
          popup.appendChild(p);
        }
        Lf.marker([s.lat, s.lng], { icon }).addTo(m).bindPopup(popup);
      });
      if (me) {
        Lf.circleMarker(me, { radius: 8, color: "#152a42", fillColor: "#4a90d9", fillOpacity: 1 }).addTo(m);
        pts.push(me);
      }
      if (pts.length > 1) m.fitBounds(pts, { padding: [30, 30] });
      else if (pts.length === 1) m.setView(pts[0], 15);
    });
    return () => {
      cancelled = true;
    };
  }, [shops, me]);

  useEffect(
    () => () => {
      map.current?.remove();
      map.current = null;
    },
    []
  );
  return <div ref={el} className="map" role="region" aria-label="Carte des magasins" />;
}
