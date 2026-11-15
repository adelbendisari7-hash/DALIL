// Service worker DALIL : application installable (F15) et listes consultables hors ligne.
const SHELL = "dalil-shell-v1";
const DATA = "dalil-data-v1";
const SHELL_URLS = ["/", "/pieces", "/manifest.webmanifest", "/icon.svg"];
// Listes de référence gardées pour la consultation hors ligne après un premier chargement.
const CACHEABLE_API = ["/vehicles/", "/parts/categories", "/shops/recommend", "/shops?", "/geo/communes"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_URLS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => ![SHELL, DATA].includes(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const isApi = url.pathname.includes("/api/v1/");
  if (isApi && !CACHEABLE_API.some((p) => (url.pathname + url.search).includes(p))) return;
  // Réseau d'abord, cache en secours : les données restent fraîches quand le réseau répond.
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok && (isApi || url.origin === self.location.origin)) {
          const copy = res.clone();
          caches.open(isApi ? DATA : SHELL).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match("/")))
  );
});
