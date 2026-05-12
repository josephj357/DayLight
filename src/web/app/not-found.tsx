import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-prose px-4 sm:px-6 lg:px-8 py-24 text-center">
      <p className="text-xs uppercase tracking-[0.18em] text-daylight-700 font-semibold">
        404
      </p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink-900">
        We don&apos;t have that page yet.
      </h1>
      <p className="mt-3 text-ink-600">
        v1 covers FL-23 / Broward County. If you&apos;re looking for another
        district, fork the repo and add your adapter.
      </p>
      <div className="mt-6 flex justify-center gap-4 text-sm">
        <Link
          href="/"
          className="font-semibold text-daylight-700 hover:text-daylight-900"
        >
          Back home
        </Link>
        <Link
          href="/district/fl-23"
          className="font-semibold text-daylight-700 hover:text-daylight-900"
        >
          See FL-23
        </Link>
      </div>
    </div>
  );
}
