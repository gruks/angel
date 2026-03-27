import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { Globe2 } from "lucide-react";

import { Providers } from "@/components/Providers";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Angel | Conflict Risk Prediction Dashboard",
  description: "UN-style conflict-risk monitoring and forecasting interface.",
};

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/heatmap", label: "Heatmap" },
  { href: "/signals", label: "Signal Explorer" },
  { href: "/backtesting", label: "Backtesting" },
  { href: "/alerts", label: "Alerts" },
  { href: "/api-docs", label: "API Docs" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-white text-black">
        <Providers>
          <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6">
            <header className="sticky top-0 z-40 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/90">
              <div className="flex items-center justify-between py-5">
                <Link href="/dashboard" className="inline-flex items-center gap-2">
                  <Globe2 className="text-[#009EDB]" size={20} />
                  <span className="text-xl font-semibold text-[#009EDB]">Angel</span>
                </Link>
                <nav className="flex flex-wrap items-center justify-end gap-2 text-sm">
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="rounded-lg px-3 py-2 text-black transition-colors duration-200 hover:bg-[#009EDB]/10 hover:text-[#009EDB]"
                    >
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </div>
              <div className="h-px bg-gray-200" />
            </header>
            <main className="flex-1 py-6">{children}</main>
            <footer className="border-t border-gray-100 py-4 text-xs text-gray-500">
              Angel conflict-risk intelligence dashboard. Data sources include ACLED, GDELT,
              UNHCR, IMF, and auxiliary public monitoring feeds.
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
