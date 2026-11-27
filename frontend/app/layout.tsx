import type { Metadata, Viewport } from "next";
import { Barlow_Condensed } from "next/font/google";
import "./globals.css";
import TopBar from "@/components/TopBar";
import { t } from "@/lib/i18n";


// Texte courant : police du système (globals.css), lisible et sans téléchargement ; Barlow Condensed pour les titres.
const display = Barlow_Condensed({ subsets: ["latin"], weight: ["700", "800"], variable: "--font-display", display: "swap" });

export const metadata: Metadata = {
  title: "DALIL",
  description: t("app.tagline"),
  manifest: "/manifest.webmanifest",
  icons: { icon: "/icon.svg", apple: "/icon.svg" },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#152a42", viewportFit: "cover" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={display.variable}>
      <body>
        <TopBar />
        <main>{children}</main>
      </body>
    </html>
  );
}
