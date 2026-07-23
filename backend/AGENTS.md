# AGENTS.md — `backend/`

> See the root `../AGENTS.md` for the full system picture. This file narrows in
> on backend-only concerns.

## Files & responsibilities

| File                       | Runs in       | Role                                                                              |
|----------------------------|---------------|-----------------------------------------------------------------------------------|
| `main.py`                  | Host venv     | FastAPI broker + asyncio TCP server (HTTP :8123, internal TCP :8890)              |
| `ue_mrp_client.py`         | UE5 Editor    | `UEMRQServer`: TCP listener + Slate post-tick + single-render MRQ execution       |
| `mrq_batch_dataset.py`     | UE5 Editor    | `AutomatedBatchGenerator` + the `apply_emotion_to_sequence_asset()` animation baker |
| `expression_profiles.json` | Both (read)   | emotion -> ControlRig control map (target/delay/easing/jitter)                    |
| `progress.json`            | UE writes, FastAPI reads | live batch progress (status/current/total/elapsed/eta)               |
| `cancel_flag.txt`          | FastAPI writes, UE reads | presence == cancel requested                                        |

## Two execution envelopes — keep them separate

- **`main.py` must import cleanly in a normal Python venv** with only `fastapi`,
  `uvicorn` (plus stdlib `asyncio`, `json`, `uuid`, `os`). It never imports
  `unreal`. Do not move `unreal`-using code up into it.
- **`ue_mrp_client.py` and `mrq_batch_dataset.py`** depend on `unreal`, which
  only exists inside the UE5 Editor's embedded interpreter. Both guard the
  `import unreal` with `try/except ImportError: pass` so the FastAPI process can
  still import the *module* (for e.g. path reasons) — but their `unreal.` calls
  will only work when executed from the UE Python console.

## Async request lifecycle (`main.py`)

- Every mutating endpoint mints a `task_id` (uuid4), stores a `loop.create_future()`
  in `active_requests[task_id]`, writes a newline-delimited JSON command to the
  single UE socket writer, and `await`s the future with a timeout
  (120s for `/api/render`, 3600s for `/api/generate_batch`).
- The UE side MUST echo `task_id` in its response JSON so the broker's
  `handle_ue_client` reader can call `active_requests[task_id].set_result(...)`.
  **Never drop or rename `task_id`** in a round trip.
- Single UE client is assumed: `writer = ue_clients[0]`. A second connect is
  appended to `ue_clients` but only index 0 is written to. Don't introduce
  load-balancing without revisiting this.
- 503 from `/api/render` and `/api/generate_batch` means `ue_clients` is empty —
  the frontend uses this specifically to pop the "connect Unreal" modal.

## UE-side execution (`ue_mrp_client.py` + `mrq_batch_dataset.py`)

- `UEMRQServer.connect()` opens a blocking socket thread (`listen_loop`) and
  registers a `unreal.register_slate_post_tick_callback(self.tick)`. Tasks are
  only processed from the main UE thread on post-tick, **one at a time**
  (`active_executor is None`). Keep this serialisation — MRQ + PIE is not
  re-entrant.
- `process_task()` branches on `task.get("command") == "generate_batch"`:
  - Single render path sets up a 450×600 PNG MRQ job on `/Game/micro_expression`
    + `/Game/final_level`, runs a `MoviePipelinePIEExecutor`, and on finish posts
    `image_url: /renders/Render_<task_id>0000.png`.
  - Batch path hot-reloads `mrq_batch_dataset` (`importlib.reload`) and spins up
    `AutomatedBatchGenerator(task)` with `on_complete_callback` wired to
    `send_response`.
- `AutomatedBatchGenerator` chains iterations via `register_slate_post_tick_callback`
  in `tick_trigger_next()`. Each iteration:
  1. checks `cancel_flag.txt` -> abort+bail to `finalize_batch()`
  2. rewrites `progress.json`
  3. bakes emotion keys (static or animated) onto the sequence
  4. allocates a fresh MRQ job (PNG for flashcards, MP4 for videos), runs PIE
  5. `on_mrq_finished` appends `current_job_metadata` to `self.database` and
     schedules the next iteration
- `finalize_batch()` dumps to `database.json` (flashcards) or `database_video.json`
  (videos) in `C:/.../webapp/public/dataset/`.

## The animation baker — `apply_emotion_to_sequence_asset()`

Pseudo-state machine per ControlRig control, per frame, when `video_timings` is
provided (video mode):

```
neutral (0)  ->  onset ramp up (ease_in_out_cubic)  ->  hold (target + sin jitter)  ->  offset ramp down  ->  neutral (0)
```

Timings: `neutral_start=0.2s`, `onset=0.08s`, `hold=hold_duration_ms`,
`offset=0.12s`, `neutral_end=0.2s`. FPS chosen by hold duration
(`<=100ms->120`, `<=250ms->60`, else `30`). Each control's `delay_ms` shifts its
own onset/offset windows. In static (flashcard) mode only frame 0 is keyed at
`target * intensity`.

**Crucial side effect:** the function first clears all existing keys and then
zeros every known float control (from `face_controlboard_controls.json`, or a
hardcoded fallback list if that file is missing) at frame 0. This prevents
emotions from previous renders leaking into the next card. Any new control you
introduce via a profile must also be listed in
`face_controlboard_controls.json` or it won't be zeroed (and will sticky-carry
into the next render).

## Gotchas specific to this directory

- **Stale port comment:** `main.py` line 8 says `--reload --port 8000`; the
  actual configured port is **8123** (confirmed by the README and the frontend's
  hardcoded `http://localhost:8123`). It's a doc bug, not a runtime bug.
- **Hardcoded absolute paths** to
  `C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\...` appear in both
  UE-side files for `face_controlboard_controls.json`, `expression_profiles.json`,
  output dirs, `progress.json`, `cancel_flag.txt`. There is no env indirection.
- **`Batch` command tagging:** `main.py:generate_batch` adds `command:
  "generate_batch"` to the payload; single renders don't add a `command` key, so
  `process_task` treats anything without that key as a single render.
- **`reload` on every batch:** `ue_mrp_client.process_task` does
  `importlib.reload(mrq_batch_dataset)` before each batch. That re-executes the
  module top-level — keep module-level side effects out of `mrq_batch_dataset`
  (it currently has none besides `import math`).
- **`progress.json` is currently checked in** (shows a mid-run snapshot). It is
  a runtime scratch file; treat as transient. Do not edit it by hand to "reset"
  things — the batch generator deletes and rewrites it on `start()`.
- **Cancellation is file-based**, not socket-based. The frontend hits
  `/api/cancel_batch`, FastAPI writes `cancel_flag.txt`, and the UE batch loop
  polls for that file at the top of each iteration. There is no mid-frame
  cancellation; an in-flight MRQ render always finishes the current job.

## Dependencies

- Host venv needs: `fastapi`, `uvicorn` (run as
  `uvicorn main:app --port 8123`). stdlib handles the rest.
- UE side needs whatever the UE5.8 embedded Python provides + `unreal`. The
  `.uproject` enables `MovieRenderPipeline`, `MoviePipelineMaskRenderPass`,
  `ModelingToolsEditorMode`, and the full MetaHuman plugin set. An `unreal-mcp`
  HTTP server is declared at `http://127.0.0.1:8000/mcp` (see root `.mcp.json`)
  — separate port from this broker.
