import type { Metadata } from "next";
import "@fontsource-variable/inter";
import "@fontsource-variable/space-grotesk";
import "./globals.css";
import { AppShell } from "@/components/app-shell";

export const metadata: Metadata = {
  title: "AdIntel — Intelligence de anúncios",
  description: "Explore criativos, scores de longevidade e sinais de escala. Ambiente MVP com dados simulados.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body><AppShell>{children}</AppShell></body>
    </html>
  );
}
