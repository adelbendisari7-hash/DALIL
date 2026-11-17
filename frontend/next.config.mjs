/** @type {import('next').NextConfig} */
// L'API est jointe par le serveur du site (même adresse que le site) : un téléphone sur le même Wi-Fi n'a
// qu'une adresse à connaître, et le navigateur n'a pas besoin d'autorisation CORS.
const API_INTERNAL = process.env.DALIL_API_INTERNAL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  distDir: process.env.NEXT_DIST_DIR || ".next",  // .next-e2e pour les tests (playwright.config.ts)
  // Le relais vers l'API abandonne par défaut au bout de 30 s : trop court si l'API vient de démarrer et charge encore
  // ses modèles, ou avec le modèle de langage activé (USE_LLM=1).
  experimental: { proxyTimeout: 120_000 },
  // Mode développement ouvert depuis un téléphone du même Wi-Fi (adresses de réseau local).
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*", "172.*.*.*"],
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${API_INTERNAL}/api/v1/:path*` }];
  },
};
export default nextConfig;
