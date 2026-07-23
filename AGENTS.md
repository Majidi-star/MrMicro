# AGENTS.md — MetaHuman Micro-Expression Training App

> This file is the canonical guide for any AI coding agent (ZCode, Codex, Claude,
> Cursor, Gemini) working in this repository. Subdirectory `AGENTS.md` files add
> narrower, scope-specific guidance. `CLAUDE.md` files exist only as pointers to
> the corresponding `AGENTS.md` (kept for tool compatibility).

## 1. What this project is

An end-to-end stack for generating and practicing **micro-expression recognition**
flashcards and videos. The pipeline bridges three decoupled tiers:

1. **React Web App (`webapp/`)** — the user-facing UI. Users practice identifying
   Action Units (AUs) and the seven fundamental emotions (ANGER, CONTEMPT,
   DISGUST, FEAR, HAPPINESS, SADNESS, SURPRISE) plus NEUTRAL. Two training modes:
   static **Flashcards** and **Video Training**.
2. **FastAPI Broker (`backend/main.py`)** — a lightweight ASGI server. It exposes
   HTTP endpoints for the React app and proxies render orders into Unreal Engine
   over an internal TCP socket (`127.0.0.1:8890`).
3. **Unreal Engine 5 TCP Executor (`backend/ue_mrp_client.py`,
   `backend/mrq_batch_dataset.py`)** — Python scripts that live **inside** the
   running UE5 Editor. They receive JSON payloads over the socket, drive the
   `Face_ControlBoard_CtrlRig` on a Level Sequence, and spawn Movie Render Queue
   (MRQ) jobs that emit PNG / MP4 frames directly into `webapp/public/dataset/`
   (or `webapp/public/renders/`).

A fourth capability: the React app can also operate purely on a **pre-rendered
static dataset** (`webapp/public/dataset/database.json` and
`database_video.json`) so the app can be hosted without a live UE instance.

## 2. Repository layout (the parts you will actually edit)

```
Metahuman/                       <- UE5 project root (Content/, Config/, Saved/, Intermediate/, *.uproject ignored in git)
├── AGENTS.md                    <- THIS file (root guidance)
├── README.md                    <- human-facing setup guide (mirrors this)
├── Metahuman.uproject           <- UE 5.8 project descriptor (plugins: MetaHuman*, MovieRenderPipeline, ModelContextProtocol, ...)
├── .mcp.json                    <- MCP server: unreal-mcp @ http://127.0.0.1:8000/mcp
├── face_controlboard_controls.json   <- source-of-truth list of Face ControlRig float controls
├── backend/
│   ├── AGENTS.md / CLAUDE.md    <- backend-specific guidance
│   ├── main.py                  <- FastAPI broker + TCP socket server (port 8123 HTTP, 8890 internal)
│   ├── ue_mrp_client.py         <- UEMRQServer: runs INSIDE UE Editor, listens on TCP, drives MRQ for single renders
│   ├── mrq_batch_dataset.py      <- automated batch generator (flashcards + videos); also the animation baker
│   ├── expression_profiles.json  <- per-emotion ControlRig target values / delays / easing / jitter
│   ├── progress.json            <- LIVE batch progress (status/current/total/elapsed/eta), polled by the frontend
│   └── cancel_flag.txt          <- presence of this file = user requested batch cancel
├── webapp/
│   ├── AGENTS.md / CLAUDE.md    <- frontend-specific guidance
│   ├── package.json             <- React 19, Vite 8, oxlint (no router, no state lib)
│   ├── vite.config.js           <- bare @vitejs/plugin-react (no custom aliases)
│   ├── src/App.jsx              <- the ENTIRE app (one ~1300-line component, no split yet)
│   ├── src/main.jsx             <- createRoot StrictMode entry
│   ├── src/index.css            <- global styles + theme variables ([data-theme="dark|light"])
│   ├── src/App.css              <- (optional) component styles
│   ├── public/dataset/          <- static database.json + database_video.json + rendered PNG/MP4 (gitignored bulk)
│   ├── public/renders/          <- single on-demand renders from the live stack
│   └── public/rig_example/1.png <- the static "visual guide" reference image shown post-submit
└── *.py (root, ~60 files)       <- one-off UE Python inspection / research scripts (see section 9)
```

> Everything UE-generated (`Content/`, `Config/`, `Saved/`, `Intermediate/`,
> `DerivedDataCache/`, `*.uproject`, binaries) is gitignored. Treat the repo as
> the **code + assets** slice of a much larger local UE5 project.

## 3. The data model contracts (do not silently break these)

### Flashcard record (`database.json` entries)
```json
{
  "image": "Flashcard_0003_HAPPINESS0000.png",   // filename in public/dataset/
  "emotions": ["HAPPINESS"],                       // [] or ["NEUTRAL"] => neutral card
  "intensity": 0.9397,                             // 0.0 - 1.0 (frontend treats *10 as a 1-10 slider)
  "controls_applied": { "CTRL_L_mouth_cornerPull": 0.9397, ... }  // ControlRig name -> value
}
```

### Video record (`database_video.json` entries)
```json
{
  "id": "Video_0001_SADNESS",
  "emotions": ["SADNESS"],
  "intensity": 0.1836,
  "controls_applied": { ... },
  "duration_ms": 100,       // hold duration; drives fps selection (<=100 -> 120fps, <=250 -> 60, else 30)
  "fps": 120,
  "total_frames": 84,
  "video_url": "Video_0001_SADNESS.mp4"   // filename in public/dataset/
}
```

**Filename convention is load-bearing.** `Flashcard_NNNN_EMOTION0000.png` and
`Video_NNNN_EMOTION.mp4` are derived from `{job_name}{frame_number}` /
`{job_name}` MRQ formats in `mrq_batch_dataset.py`. The frontend does NOT parse
filenames today, but the on-demand render path in `ue_mrp_client.py` returns
`image_url: /renders/Render_<task_id>0000.png` — keep that suffix in sync if you
touch either side.

**"NEUTRAL" handling is subtle.** A neutral record has `emotions: []` (empty)
in the DB, but the UI lists a literal `"NEUTRAL"` string button. `getNeutralUrl`
in `App.jsx` finds the neutral card by empty emotions OR `"NEUTRAL"` membership.
`reshuffleDeckWithFilters` deliberately **excludes** neutral cards from the deck
(neutrals are only used as the comparison baseline). Preserve this when
filtering.

### The emotion -> ControlRig mapping (single source of truth)
`backend/expression_profiles.json` defines, per emotion, which
`CTRL_*_...` float controls fire, with `target` (0-1), `delay_ms`, `easing`
(`linear`|`cubic`), and `jitter` amplitude. `mrq_batch_dataset.py` reads this at
render time and bakes per-frame keys onto the ControlRig Parameter Section of
the sequence. A fallback map exists in code for any missing emotion. The list of
valid control names lives in `face_controlboard_controls.json` (filter to
`type == "FLOAT"`).

## 4. How the traffic flows (end to end)

### Live single render (Flashcards / on-demand image)
```
React  POST http://localhost:8123/api/render {emotion, intensity, aus}
  -> main.py: render_image()
     - assigns task_id, stashes a Future in active_requests[task_id]
     - writes JSON line to the connected UE socket writer
  -> [TCP 8890] ue_mrp_client.UEMRQServer.listen_loop() enqueues task
  -> UE post-tick -> process_task()
     - apply_emotion_to_sequence_asset("/Game/micro_expression", emotion, intensity/10)
     - builds MRQ job (map "/Game/final_level", 450x600 PNG portrait), runs PIE executor
  -> on_mrq_finished() -> send_response({task_id, status, image_url: /renders/<file>})
  -> [TCP back] main.py resolves the Future, returns JSON to React
```

### Batch generation (Database tab)
```
React POST /api/generate_batch {type, hold_duration_ms, num_images, intensity_min/max,
                                quality, emotion_weights}
  -> main.py pins command="generate_batch", 1-hour timeout Future
  -> UE: process_task() sees command, spins up AutomatedBatchGenerator(task)
  -> generator runs one MRQ job per iteration, driven by Slate post-tick callbacks
     - writes progress.json each iteration  (polled every 500ms by React via /api/batch_progress)
     - checks for cancel_flag.txt each iteration  (React writes it via POST /api/cancel_batch)
     - appends metadata to self.database
  -> finalize_batch() dumps database.json (flashcards) OR database_video.json (videos)
  -> on_complete_callback -> send_response -> Future resolves -> React reloads datasets
```

### Static-only mode (no UE running)
React fetches `/dataset/database.json` and `/dataset/database_video.json`
directly from the Vite-served `public/` folder. No network calls to port 8123
unless the user hits the Database ▸ "COMMENCE UNREAL BATCH GENERATION" button
(which will 503 with a connect-modal if UE is offline).

## 5. Running the stack (the three-window dance)

1. **Backend broker** —
   `cd backend && uvicorn main:app --port 8123` (note: README says 8123; the
   comment in `main.py` line 8 mentions 8000 but the configured port is 8123 and
   the frontend hardcodes `http://localhost:8123`). On startup it also opens the
   internal TCP server on `127.0.0.1:8890`.
2. **Unreal Engine 5.8** — open `Metahuman.uproject`, load `final_level.umap`.
   In the Output Log switch the command bar to `Python` and run:
   ```python
   import sys, importlib
   sys.path.append(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend")
   import ue_mrp_client; importlib.reload(ue_mrp_client)
   import mrq_batch_dataset; importlib.reload(mrq_batch_dataset)
   server = ue_mrp_client.UEMRQServer(); server.connect()
   ```
   Success log appears in both the UE log and the FastAPI terminal.
3. **Frontend** — `cd webapp && npm run dev` (Vite dev server, default
   `http://localhost:5173`).

**Hardcoded absolute paths** appear in `main.py` (`progress.json`,
`cancel_flag.txt`) and across `ue_mrp_client.py` / `mrq_batch_dataset.py`
(`face_controlboard_controls.json`, `expression_profiles.json`, the
`webapp/public/...` output dirs). These point at
`C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\...`. If you relocate
the project, update these literals (there is no config indirection yet — a
worthwhile refactor target).

## 6. API surface (FastAPI, `backend/main.py`)

| Method | Path                       | Purpose                                                      |
|--------|----------------------------|--------------------------------------------------------------|
| GET    | `/`                        | Health check: `{status, ue_connected: bool}`               |
| POST   | `/api/render`              | Single on-demand render; 120s timeout; 503 if UE offline     |
| POST   | `/api/generate_batch`      | Batch generation; 3600s timeout; pins `command=generate_batch` |
| GET    | `/api/batch_progress`      | Reads `backend/progress.json`; `{status: "idle"}` if absent  |
| POST   | `/api/cancel_batch`        | Writes `backend/cancel_flag.txt` = `"CANCEL"`                |

CORS is wide open (`allow_origins=["*"]`). Single connected UE client is
assumed (`ue_clients[0]`); a second concurrent UE connection is tolerated by the
list but the response routing is keyed on `task_id` so it still works.

## 7. Frontend conventions (`webapp/`)

- **Stack:** React 19 + Vite 8 + oxlint. No router, no Redux/Zustand — all state
  is local `useState` in the single `App` component. No CSS-in-JS — styles are a
  mix of `index.css` class names and inline `style={}` props.
- **The monolith:** `src/App.jsx` is the entire app (~1290 lines). Tabs:
  `TUTORIAL`, `FLASHCARDS`, `VIDEO_TRAINING`, `ABOUT`. A `Settings` modal has
  sections `General | Flashcards | Video Training | Database`.
- **Theming:** `document.documentElement.setAttribute('data-theme',
  theme.toLowerCase())`. CSS variables are consumed as `var(--accent-blue)`,
  `var(--text-main)`, `var(--text-muted)`, `var(--bg-panel)`, `var(--bg-input)`,
  `var(--border-color)`, `var(--settings-border)`. Keep new components on these
  tokens.
- **Backend URL is hardcoded** to `http://localhost:8123` in several `fetch`
  calls (batch progress, generate, cancel). Introduce a `VITE_API_BASE` env if
  you need to detach, rather than scattering more literals.
- **Deck mechanics:** both flashcards and videos use a Fisher-Yates shuffled
  `deck` array + a `drawnIndices` stack for Previous/Next navigation. A card is
  "neutral" iff `entry.emotions.length === 0 || entry.emotions.includes("NEUTRAL")`.
- **Comparison slider** in post-submit uses `sliderValue` (0-100) to clip the
  neutral image over the expression image. The visual guide panel always shows
  `/rig_example/1.png` for flashcards; for videos it shows the same MP4 paused
  at `getPeakTimestamp()` = 0.28s (neutral_start 0.2s + onset 0.08s).
- **Lint:** `npm run lint` runs oxlint (config in `.oxlintrc.json`).
- **Build:** `npm run build` -> `dist/`. `npm run preview` serves the build.

See `webapp/AGENTS.md` for component/state specifics you'll trip over.

## 8. Backend conventions (`backend/`)

- `unreal` is **not pip-installable**; it only exists inside the UE Editor's
  embedded Python. Every backend module guards `import unreal` with
  `try/except ImportError: pass` so the same files can be imported by the FastAPI
  broker (which never touches `unreal`) and by the UE Python console.
  **Consequence:** `main.py` runs in a normal venv; `ue_mrp_client.py` and
  `mrq_batch_dataset.py` run inside UE. Don't add top-level code that assumes
  `unreal` is present.
- Render execution uses `unreal.MoviePipelinePIEExecutor` (Play-In-Editor).
  Expect the editor UI to lock up during batches — README explicitly warns users
  not to touch the engine mid-generation.
- `apply_emotion_to_sequence_asset()` is the animation core: it clears existing
  keys, zero-initializes all known float controls at frame 0 (anti
  cross-contamination), then either keys a single frame (flashcards) or bakes a
  per-frame neutral→onset→hold(+jitter)→offset→neutral curve (videos) driven by
  `ease_in_out_cubic` and the timings in `calculate_video_timings()`.
- Async pattern: `main.py` pairs each request with a `loop.create_future()` keyed
  by `task_id`; the UE side echoes `task_id` back in its JSON response so the
  broker can resolve the right future. Keep `task_id` round-tripping intact.

See `backend/AGENTS.md` for the UE-side specifics.

## 9. The root `*.py` research scripts

The repo root has ~60 single-purpose Python scripts (`inspect_*.py`,
`test_*.py`, `get_*.py`, `evaluate_*.py`, plus matching `*_output.txt` dumps).
These are **one-off exploration tools** the author ran inside UE's Python
console while reverse-engineering the ControlRig / MRQ / DNA / Sequencer APIs.
They are gitignored as scratch (the `*.txt` outputs are covered by `*.txt` in
`.gitignore`). Treat them as reference material, not production code:

- Don't build features depending on them.
- It's fine to read them to learn which UE classes/methods are valid
  (`unreal.MovieSceneControlRigParameterSection`, `unreal.MoviePipeline*`, etc).
- The two **git-tracked** data files — `face_controlboard_controls.json` and
  `pose_interrogation_results.json` — are kept via `!` negations in `.gitignore`.

## 10. Agent workflow rules

1. **Match the existing idiom.** Backend Python uses plain functions, `try/
   except` around every `unreal` call, and `unreal.log/log_warning/log_error`
   for diagnostics. Frontend uses inline-style JSX objects and CSS-variable
   theme tokens — don't introduce a CSS framework mid-feature.
2. **Never assume `unreal` imports in `main.py`.** `main.py` is the only file
   that must stay importable in a bare Python venv.
3. **Keep contracts in sync.** If you add a field to `database*.json`, update
   both the writer (`mrq_batch_dataset.py`) and the reader (`App.jsx`). If you
   add an emotion, add it to `expression_profiles.json` *and* the fallback map
   *and* the frontend `emotions` array.
4. **Touch the absolute paths consciously.** There are ~6 hardcoded
   `C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\...` literals with
   no indirection. Changing the project location means editing each.
5. **Running anything live requires a running UE5 instance** on the same
   machine, loaded into `final_level.umap`, with the TCP server connected. You
   cannot smoke-test the render path headlessly. The static-dataset path
   (load `database*.json` from `public/`) CAN be tested with just
   `npm run dev`.
6. **MCP:** an `unreal-mcp` HTTP server is declared at
   `http://127.0.0.1:8000/mcp` (in `.mcp.json`, `.cursor/mcp.json`,
   `.codex/config.toml`, `.gemini/settings.json`, `.vscode/mcp.json`). Note this
   is port **8000**, distinct from the FastAPI broker on **8123** and the
   internal TCP on **8890**. Whether that MCP server is running depends on the
   UE side — don't assume it's up.
7. **Don't commit generated bulk.** `webapp/public/dataset/*.png`,
   `database.json`, and `webapp/public/renders/*` are gitignored on purpose
   (gigabytes). `database.json` / `database_video.json` are intentionally
   gitignored too; the small sample currently in tree was committed before the
   ignore rule broadened — leave it unless told otherwise.

## 11. Good first refactor targets (call them out to the user, don't auto-do)

- **Split `webapp/src/App.jsx`** into `tabs/Flashcards.jsx`,
  `tabs/VideoTraining.jsx`, `components/SettingsModal.jsx`,
  `components/ComparisonSlider.jsx`, `lib/dataset.js` (load/reshuffle/filter),
  `lib/api.js` (fetch base + endpoints). Currently one giant component.
- **Introduce a `VITE_API_BASE`** env var to replace the hardcoded
  `http://localhost:8123`.
- **Externalise the hardcoded absolute paths** into a `backend/paths.py` or
  read from an env var / `sys.argv`.
- **Port note in `main.py`** is stale (`--port 8000` comment vs actual 8123) —
  trivial doc fix.
- **Dual-source for emotion->controls** (the JSON profile vs the in-code
  fallback map in `mrq_batch_dataset.py`). Unify by always reading the JSON.
