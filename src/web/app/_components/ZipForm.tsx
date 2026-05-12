"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { MapPin, Loader2 } from "lucide-react";
import { resolveZip } from "@/lib/api";

/**
 * Landing-page ZIP entry.
 *
 * v1: hardcoded 33064 → /district/fl-23 (via resolveZip's static fallback).
 * If backend is up, /search/zip/{zip} is used.
 */
export function ZipForm() {
  const router = useRouter();
  const [zip, setZip] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const trimmed = zip.trim();
    if (!/^\d{5}$/.test(trimmed)) {
      setError("Please enter a 5-digit ZIP code.");
      return;
    }
    setLoading(true);
    try {
      const result = await resolveZip(trimmed);
      if (result?.districtId) {
        router.push(`/district/${result.districtId}`);
      } else {
        setError(
          "We don't cover this ZIP yet. Try 33064 for the v1 demo (Broward County, FL).",
        );
        setLoading(false);
      }
    } catch {
      setError("Couldn't reach the lookup. Try again in a moment.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate>
      <label htmlFor="zip" className="sr-only">
        Enter your ZIP code
      </label>
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <MapPin
            className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-400"
            aria-hidden="true"
          />
          <input
            id="zip"
            type="text"
            inputMode="numeric"
            pattern="[0-9]{5}"
            maxLength={5}
            placeholder="Enter ZIP code (try 33064)"
            value={zip}
            onChange={(e) => setZip(e.target.value.replace(/[^0-9]/g, ""))}
            className="w-full rounded-lg border border-ink-300 bg-white py-3 pl-9 pr-3 text-base shadow-sm placeholder:text-ink-400 focus:border-daylight-500 focus:outline-none focus:ring-2 focus:ring-daylight-300"
            aria-describedby={error ? "zip-error" : undefined}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-ink-900 px-5 py-3 text-sm font-semibold text-white hover:bg-ink-800 focus:outline-none focus:ring-2 focus:ring-daylight-400 disabled:opacity-60"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : null}
          See my ballot
        </button>
      </div>
      {error && (
        <p
          id="zip-error"
          role="alert"
          className="mt-2 text-sm text-flag-alignment"
        >
          {error}
        </p>
      )}
    </form>
  );
}
