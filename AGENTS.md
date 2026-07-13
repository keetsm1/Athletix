# Athletix

Two independent apps under `apps/`: **web** (Next.js 16, React 19, Tailwind v4, TypeScript) and **backend** (Python 3.14 data ingestion scripts into Supabase). No monorepo tooling, no root package.json, no workspaces.

## Repo-level

- `.env` files in both `apps/web/` and `apps/backend/` are **committed with live secrets** (Supabase service key, API keys). Do not commit new secrets — the existing ones are already tracked.
- No root-level scripts — always `cd apps/web` or `cd apps/backend` first.

## Web (`apps/web`)

- `npm run dev` — dev server on localhost:3000
- `npm run build` — production build (runs typecheck implicitly)
- `npm run lint` — ESLint 9 flat config (`eslint.config.mjs`)
- Auth: `@supabase/ssr`, email/password only. No middleware, no session persistence yet.
- Tailwind v4 uses CSS-first config: `@import "tailwindcss"` in `globals.css` + `@tailwindcss/postcss` plugin. No `tailwind.config.js`.
- Page pattern: component lives in a named `.tsx`, `page.tsx` re-exports it.

## Backend (`apps/backend`)

- No dependency manifest (`requirements.txt` or `pyproject.toml`). Reproduce venv via `pip install supabase nba_api eplda pandas requests python-dotenv httpx`.
- Activate: `source apps/backend/.venv/bin/activate`
- Run scripts directly: `python scripts/player_data/epl_players.py`

### Data pipeline (run order matters)

1. **Teams first**: `epl_teams.py` → `nba_teams.py` → `nhl_teams.py` populates the `teams` table.
2. **Then players**: `nhl_player.py` → `nba_players.py` → `epl_players.py` populates the `players` table.

### Player script quirks

- **EPL** (`epl_players.py`): Uses `eplda` library + PulseLive API (reverse-engineered from premierleague.com, no key). **Deletes all existing EPL players before upsert.** Has hardcoded club abbreviation mappings (`CLUB_ABBR_MAP`, `PULSE_TO_SUPABASE_ABBR`) — keep in sync with supabase `teams` table. Rate-limited: sleeps 0.15s per player + 1s every 50.
- **NBA** (`nba_players.py`): 0.2s delay per player, 1s every 50. Uses `nba_api` library (public stats.nba.com).
- **NHL** (`nhl_player.py`): 0.2s delay per team. Public API at `api-web.nhle.com`, no key.

### EPL season quirk

`eplda.get_season_id()` with no arg returns the latest (currently 841 = 2026/27). The `eplda.get_player_list()` filters out players with `currentTeam=null` (players not yet registered for the upcoming season). The script has a fallback that checks those null-team players individually via PulseLive and includes ones assigned to PL clubs. If new players are missing, they likely have `currentTeam=null` and need similar handling.

### Supabase

- Backend uses `components/supabase.py` — module-level singleton with **service role key** (bypasses RLS). Use for all data scripts.
- Tables: `teams` (league, name, city, abbreviation, logo_url), `players` (league, team_id FK, first_name, last_name, full_name, position, nationality, height_cm, weight_kg, active, headshot_url).
- Web uses `app/components/supabase/supabase.tsx` — anon key (RLS-enforced), for auth only.

### Security note

The backend service key grants full database access. Treat the `.env` file as sensitive.
