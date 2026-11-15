import type { Metadata, Viewport } from "next";
import { Barlow, Barlow_Condensed } from "next/font/google";
import "./globals.css";
import TopBar from "@/components/TopBar";
import { t } from "@/lib/i18n";


const body = Barlow({ subsets: ["latin"], weight: ["400", "600", "700"], variable: "--font-body", display: "swap" });
const display = Barlow_Condensed({ subsets: ["latin"], weight: ["700", "800"], variable: "--font-display", display: "swap" });

export const metadata: Metadata = {
  title: "DALIL",
  description: t("app.tagline"),
  manifest: "/manifest.webmanifest",
  icons: { icon: "/icon.svg", apple: "/icon.svg" },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#152a42" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${body.variable} ${display.variable}`}>
      <body>
        <TopBar />
        <main>{children}</main>
      </body>
    </html>
  );
}
