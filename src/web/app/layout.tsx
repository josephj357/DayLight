import type { Metadata } from "next";
import Link from "next/link";
import { Sun, Github } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "DayLight — Daylight on money in politics.",
  description:
    "See who funds the politicians on your ballot. Federal down to school board.",
  metadataBase: new URL("https://daylight.local"),
  openGraph: {
    title: "DayLight",
    description: "Daylight on money in politics.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-ink-50 text-ink-900 font-sans">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}

function SiteHeader() {
  return (
    <header className="border-b border-ink-200 bg-white/80 backdrop-blur sticky top-0 z-30">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 group"
          aria-label="DayLight home"
        >
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-daylight-100 text-daylight-700 ring-1 ring-daylight-300 group-hover:ring-daylight-500 transition">
            <Sun className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="flex flex-col leading-tight">
            <span className="font-semibold tracking-tight text-ink-900">
              DayLight
            </span>
            <span className="text-[11px] text-ink-500 hidden sm:inline">
              Daylight on money in politics.
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          <Link
            href="/methodology"
            className="text-ink-600 hover:text-ink-900"
          >
            Methodology
          </Link>
          <a
            href="https://github.com/orka-labs/daylight"
            className="text-ink-600 hover:text-ink-900 inline-flex items-center gap-1"
            target="_blank"
            rel="noreferrer"
          >
            <Github className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
        </nav>
      </div>
    </header>
  );
}

function SiteFooter() {
  return (
    <footer className="mt-16 border-t border-ink-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-10 grid gap-6 sm:grid-cols-3 text-sm text-ink-600">
        <div>
          <p className="font-semibold text-ink-900">DayLight</p>
          <p className="mt-1 text-ink-500">Daylight on money in politics.</p>
          <p className="mt-3 text-xs text-ink-500">
            This is a gift. Free to fork. Free to improve.
          </p>
        </div>
        <div>
          <p className="font-semibold text-ink-900">Open source</p>
          <ul className="mt-1 space-y-1">
            <li>
              <a
                href="https://github.com/orka-labs/daylight"
                className="hover:text-ink-900"
                target="_blank"
                rel="noreferrer"
              >
                GitHub repository
              </a>
            </li>
            <li>
              <Link href="/methodology" className="hover:text-ink-900">
                Methodology
              </Link>
            </li>
            <li>
              <a
                href="https://www.gnu.org/licenses/agpl-3.0.html"
                className="hover:text-ink-900"
                target="_blank"
                rel="noreferrer"
              >
                License: AGPL-3.0
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-ink-900">Sources</p>
          <ul className="mt-1 space-y-1">
            <li>FEC — federal campaign finance</li>
            <li>Congress.gov API — votes</li>
            <li>OpenSecrets — industry rollups</li>
            <li>FL Division of Elections — state/local</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-ink-200 py-4 text-center text-xs text-ink-500">
        Released as a gift under AGPL-3.0. Maintained by the community.
      </div>
    </footer>
  );
}
