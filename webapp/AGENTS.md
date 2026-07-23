# AGENTS.md — `webapp/`

> See `../AGENTS.md` for the full system picture. This file narrows in on
> frontend-only concerns.

## Stack

- **React 19** (`react@^19.2.7`, `react-dom@^19.2.7`) via Vite 8
  (`vite@^8.1.1` + `@vitejs/plugin-react@^6.0.3`).
- **oxlint** for linting (`npm run lint`), config in `.oxlintrc.json`. No ESLint,
  no Prettier, no TS — this is plain JSX.
- **No router** (tab state lives in `activeTab`), **no state library** (all
  useState in `App`), **no CSS-in-JS** (global `index.css` + inline `style`s).
- `vite.config.js` is the stock `react()` plugin only — no path aliases. Import
  via relative paths.

## Source map

- `src/main.jsx` — `createRoot(...).render(<StrictMode><App/></StrictMode>)`. The
  standard Vite entry.
- `src/App.jsx` — **the entire application in one component (~1290 lines)**.
  This is the file you will spend most of your time in.
- `src/index.css` / `src/App.css` — styles. `index.css` defines the theme
  variables consumed via `[data-theme="dark|light"]` on `<html>`.
- `public/dataset/` — the static dataset (`database.json`,
  `database_video.json`, rendered `Flashcard_*.png` / `Video_*.mp4`). Served at
  `/dataset/...` by Vite. **Bulk image/video files are gitignored.**
- `public/renders/` — on-demand single renders from the live stack, served at
  `/renders/...`. Gitignored bulk.
- `public/rig_example/1.png` — the static "Visual Guide" image shown in the
  post-submit guide panel for flashcards.
- `public/favicon.svg`, `public/icons.svg` — assets.

## App.jsx anatomy

Top-level state groups (in declaration order inside `App()`):

1. **Tab + flashcard UI state:** `activeTab`, `selectedEmotions`,
   `selectedAUs`, `displayMode` (`Comparison` | `Static` | `Timed`),
   `flashDuration`, `isFlashing`, `hasSubmitted`, `sliderValue`, refs for the
   flash timer.
2. **Flashcard settings + dataset:** `intensityMin/Max`, `speed`, `difficulty`,
   `theme`, `datasetCache`, `deck`, `drawnIndices`, `reviewedCount`,
   `currentFlashcard`, `globalNeutral`, plus empty/deck-completed flags.
3. **Video training state:** mirrors of the above prefixed `video*`
   (`videoDatasetCache`, `videoDeck`, `currentVideo`, `videoDrawnIndices`...) plus
   HTML5 `<video>` refs (`videoRef`, `guideVideoRef`) and playback state
   (`videoIsPlaying`, `videoPlaybackSpeed`, `videoCurrentTime`,
   `videoDuration`).
4. **Lighting / batch settings:** `lightYaw`, `lightPitch`, `datasetType`,
   `dbVideoHoldDuration`, `batchSize`, `batchIntensityMin/Max`, `batchQuality`,
   `emotionWeights`, `isBatching`, `batchProgress`.
5. **Display chrome:** `viewingImage` (`NEUTRAL` | `EXPRESSION`), `isLoading`,
   `isSettingsOpen`, `activeSettingsTab`, `zoomMain`, `zoomGuide`,
   `showConnectModal`, `autoFlashEnabled`, `autoFlashDelay`.

The four tabs rendered conditionally in `<main>`:

- `TUTORIAL` — placeholder.
- `FLASHCARDS` — pre-submit "guessing" workflow OR post-submit
  comparison-slider + visual-guide + results strip. Uses four boolean bucket
  states: dataset empty / range empty / deck completed / `!hasSubmitted` /
  post-submit.
- `VIDEO_TRAINING` — same four-state shape but driven by `<video>` elements and
  the `video*` state group. The pre-submit timeline scrubber is **disabled**;
  post-submit unlocks play/pause, replay, 1.0x/0.5x/0.25x speed, and scrubbing.
- `ABOUT` — renders the `<ConnectionInstructions/>` component (bottom of the
  file) describing the three-window startup dance. Identical JSX also powers the
  `showConnectModal` overlay.

`<ConnectionInstructions/>` is a stateless component defined above `App()`.

## Dataset loading & deck mechanics

- `loadDataset()` and `loadVideoDataset()` fetch
  `/dataset/database{,_video}.json?<timestamp>` (cache-busted with a Date.now
  query string) on mount, then call the reshufflers.
- `reshuffleDeckWithFilters(cache)` / `reshuffleVideoDeckWithFilters(cache)`:
  - Filter the cache to NON-neutral entries whose `intensity*10` falls inside
    `[intensityMin-0.05, intensityMax+0.05]`. Video adds a second filter:
    `entry.duration_ms === videoHoldDuration`.
  - Fisher-Yates shuffle the surviving indices, pop the first into
    `currentFlashcard` / `currentVideo`, keep the rest as `deck` / `videoDeck`.
  - On empty result: set the `_isRangeEmpty` flag and show the "no images/videos
    in range" panel.
- `handleNextImage` / `handlePrevImage` (and video equivalents) push the current
  `dbIndex` onto `drawnIndices` (the back-stack) and pop the next from `deck`
  (or vice versa for Previous). `reviewedCount` is a 1-indexed display counter.

**When you change settings**, the effect `useEffect(()=>{ if (!isSettingsOpen)
{ reshuffleDeckWithFilters(); reshuffleVideoDeckWithFilters(); } },
[isSettingsOpen])` re-shuffles both decks after the modal closes. The Settings
modal also has explicit "RESHUFFLE DECK NOW" buttons that call the same
reshufflers + close the modal.

## Difficulty -> intensity mapping (two copies, keep in sync)

`handleDifficultyChange(diff)` and `handleVideoDifficultyChange(diff)` both map:

```
VeryEasy [9,10]  Easy [7,9]  Novice [6,8]  Beginner [5,7]
Intermediate [4,7]  Advanced [3,5]  Expert [2,4]
Master [1,3]  Grandmaster [1,2]
```

The video version additionally maps hold duration in ms:
`VeryEasy 500, Easy 250, Novice 200, Beginner 150, Intermediate 100, Advanced 80,
Expert 60, Master/Grandmaster 50`. These magic-number tables are duplicated —
extracting them to a `lib/difficulty.js` is a clean refactor.

## Backend integration (hardcoded)

The frontend talks to the FastAPI broker at `http://localhost:8123`. All three
calls are hardcoded literals:
- `GET http://localhost:8123/api/batch_progress` (polled every 500ms while
  `isBatching`) — drives the progress bar + ETA.
- `POST http://localhost:8123/api/generate_batch` — the "COMMENCE UNREAL BATCH
  GENERATION" button. A 503 pops `showConnectModal`.
- `POST http://localhost:8123/api/cancel_batch` — the red cancel button; then
  reloads both datasets.

A single-render `/api/render` endpoint exists on the backend but the current
flashcard/video flows only use the pre-rendered static datasets on disk — the
live single-render path is wired in the backend but not currently invoked from
the UI. (If you revive it, the response shape is
`{task_id, status, image_url: /renders/<file>}`.)

## Styling rules (match these)

- Theme is toggled by `document.documentElement.setAttribute('data-theme',
  theme.toLowerCase())`. Read tokens with `var(--accent-blue)`,
  `var(--text-main)`, `var(--text-muted)`, `var(--bg-panel)`, `var(--bg-input)`,
  `var(--border-color)`, `var(--settings-border)`.
- Existing controls use classes: `claude-select`, `claude-slider`,
  `dual-range-container`/`dual-range-track`/`dual-range-input` (the two-thumb
  range slider pattern), `submit-btn`, `toggle-btn`, `emotion-btn`
  (`+ .selected`), `nav-btn` (`+ .primary`), `video-btn`, `speed-btn`
  (`+ .active`), `video-scrubber` (`.active` unlocks), `massive-image-arena`
  (`.duo` for the side-by-side post-submit layout), `comparison-slider` /
  `slider-clip` / `slider-divider` / `slider-label-*` / `slider-legend`.
- New components should keep using these tokens and classes; avoid introducing a
  CSS framework mid-stream.

## Common edits & their blast radius

| You want to...                                  | Touch                                                                       |
|--------------------------------------------------|-----------------------------------------------------------------------------|
| Add an emotion                                   | `emotions[]` array (App.jsx:4), `expression_profiles.json` (backend), fallback map in `mrq_batch_dataset.py` |
| Add an Action Unit chip                          | `allAUs[]` (App.jsx:5)                                                      |
| Add a Settings tab                                | Sidebar items + a `{activeSettingsTab === 'X' && (...)}` block in `.settings-content` |
| Change the comparison-slider behavior            | `sliderValue` state + the `.comparison-slider` JSX in post-submit flashcard flow |
| Change video peak-frame timestamp                | `getPeakTimestamp()` (currently hardcoded `0.28`)                            |
| Point at a different backend                     | Replace the `http://localhost:8123` literals (batch_progress, generate, cancel) — or introduce `VITE_API_BASE` |
| Reset the deck when a NEW card arrives           | The `handleNext*`/`handlePrev*` functions (they carefully carry `dbIndex` between `deck` and `drawnIndices`) |

## Plan-mode refactor suggestions (don't auto-apply)

- Split `App.jsx` into `tabs/Flashcards.jsx`, `tabs/VideoTraining.jsx`,
  `components/SettingsModal.jsx`, `components/ComparisonSlider.jsx`,
  `lib/dataset.js` (load/reshuffle/filter), `lib/difficulty.js` (the shared
  mapping tables), `lib/api.js`.
- The flashcard vs video flows are ~70% structural duplicates; a shared
  `useTrainingDeck({ cache, filters, ... })` hook would eliminate most of it.
- Introduce `VITE_API_BASE` env so the backend URL isn't a literal x3.
