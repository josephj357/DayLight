# DayLight — Web

The Next.js 14 frontend for [DayLight](https://github.com/orka-labs/daylight),
an open-source civic transparency app. AGPL-3.0.

This package shows voters who funds the politicians on their ballot — federal
down to school board. v1 covers FL-23 (Broward County, FL) and every
down-ballot race a FL-23 voter sees.

## Local development

```bash
cd src/web
npm install
npm run dev
# open http://localhost:3000
```

The backend FastAPI service should be running on `http://localhost:8000`
(the default, see `/src/api`). If it isn't, the UI falls back to mock
fixtures from `lib/mock.ts` so you can develop the frontend standalone.

To point at a different backend:

```bash
NEXT_PUBLIC_API_BASE=https://api.example.com npm run dev
```

## Scripts

| Script | What it does |
|---|---|
| `npm run dev` | Next dev server on port 3000 |
| `npm run build` | Production build |
| `npm run start` | Run the production build |
| `npm run lint` | ESLint via `next lint` |
| `npm run typecheck` | `tsc --noEmit` (strict) |

## Routes

| Route | Purpose |
|---|---|
| `/` | Landing — hero, ZIP form, fork pitch |
| `/district/fl-23` | All races for a district, federal → soil & water |
| `/candidate/[id]` | Candidate deep dive (donors, industries, synthesis, votes) |
| `/methodology` | Data sources, alignment-flag logic, gaps |

## Backend API contract assumed

Defined in `lib/api.ts`. Routes the UI calls:

- `GET /districts/{id}` → `District`
- `GET /candidates/{id}` → `CandidateDetail`
- `GET /search/zip/{zip}` → `{ districtId: string } | null`

If `/src/schema/types.ts` is produced by the architect, swap the local
types for the canonical ones.

## Design principles

- **Mobile-first.** Most voters are on phones.
- **Neutral palette.** Gold/amber + warm grays. No partisan red/blue
  dominance. Every party gets the same visual footprint.
- **Editorial synthesis.** The plain-English summary uses a serif and reads
  like an editor's note — not a marketing card.
- **Accessibility.** WCAG AA contrast, semantic HTML, alt text on charts.
- **No CDN deps in the core flow.** Tailwind locally compiled, system-font
  fallbacks.
