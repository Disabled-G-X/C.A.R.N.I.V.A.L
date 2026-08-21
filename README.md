# C.A.R.N.I.V.A.L

**C**ognitive **A**ssistant & **R**esponsive **N**atural-language **I**nterface for
**V**oice-**A**ctivated **L**iving

A personalised, voice-first AI assistant built on **Google Gemini**, with a
futuristic purple dashboard, real-time system monitoring, extensible skills, and
tool-use (function calling). It is a clean re-implementation and merge of several
open-source J.A.R.V.I.S models, using **Mark-LI-main** as the architectural base.

---

## 1. Features

- **Gemini core engine** — `gemini-2.0-flash` by default (configurable), with
  streaming responses, function calling / tool use, exponential-backoff retries,
  timeout handling, and rate-limit awareness. API key read from `GEMINI_API_KEY`.
  Changing the model in Settings hot-rebuilds the client — no restart needed.
- **Voice-first** — wake word ("Hey Carnival" / "Carnival") + Web Speech API in
  the browser, barge-in (TTS stops when you start talking); optional headless
  mic mode (`python main.py --voice`).
- **Futuristic purple UI** — dark gradient theme, glowing voice waveform,
  chat bubbles with timestamps, live system dashboard, settings panel, log viewer,
  typing indicator, tool-execution chips, alert chimes, and a conversation
  toolbar (clear / export transcript as Markdown / rescan skills).
- **Extensible skills** — drop a single `.py` file into `carnival/skills/` (or
  `carnival/data/skills/`) and it becomes a Gemini tool on next launch. User
  skills override built-ins of the same name. Start from `_template.py`.
- **QoL skills** — system monitor (incl. battery), web search (Gemini grounded +
  DDG fallback), weather, reminders/timers (persisted & re-armed across
  restarts), app launcher, file ops, YouTube, notes/to-dos, music, Wikipedia,
  translate, calculator, smart-home (TP-Link Kasa), daily briefing (time +
  system + weather + news), volume/brightness control, screenshots, clipboard,
  process manager (top consumers / kill), machine info — plus a sandboxed shell
  (off by default).
- **Conversation memory** — the chat is persisted to disk and restored into
  context after a restart; clear it any time from the UI.
- **Self-test** — `python main.py --check` verifies dependencies, config, all
  skills, and the agent loop without spending API quota. A pytest suite lives
  in `tests/` (`pip install -r requirements-dev.txt && python -m pytest tests/`).
- **Async / responsive** — Flask + Socket.IO streams tokens, metrics, and logs
  without blocking the UI.

---

## 2. Quick start

```bash
cd /var/home/obsycronite/C.A.R.N.I.V.A.L
./start.sh                     # creates .venv + .env on first run, then launches
```

or manually:

```bash
cd /var/home/obsycronite/C.A.R.N.I.V.A.L
python -m venv .venv && source .venv/bin/activate     # recommended
pip install -r requirements.txt

cp .env.example .env
# edit .env and set:  GEMINI_API_KEY=your_real_key

python main.py --check         # optional: verify everything first
python main.py                 # launches dashboard at http://127.0.0.1:8000
```

Open the URL in Chrome/Edge. Allow microphone access for voice. Say
**"Hey Carnival"** then your command, or just type.

Other modes:

```bash
python main.py --text         # terminal chat loop (no browser needed)
python main.py --voice        # headless voice (mic + TTS)
python main.py --skills       # list discovered skills
python main.py --check        # self-test (deps, config, skills, agent loop)
python main.py --version
python main.py --host 0.0.0.0 --port 9000
```

Keyboard shortcuts: **Ctrl+/** focuses the composer, **Esc** closes Settings.

---

## 3. Configuration

| Key | Where | Default | Notes |
|---|---|---|---|
| `GEMINI_API_KEY` | env / `.env` | — | **Required.** Never hardcoded. |
| `GEMINI_MODEL` | env / settings | `gemini-2.0-flash` | Any Gemini model id. |
| `CARNIVAL_NAME` | env / settings | `Carnival` | Assistant name. |
| `CARNIVAL_TTS` | env / settings | `browser` | `browser` \| `edge` \| `pyttsx3`. |
| `OPENWEATHER_API_KEY` | env / settings | — | Upgrades weather skill. |

All other settings (wake word, theme, module toggles, voice) live in
`carnival/data/settings.json` and are editable from the in-app **Settings** panel.

### Themes
`midnight` (default), `neon`, `royal` — switch from the Settings panel.

---

## 4. Architecture

```
 Browser (purple UI)
   │  Socket.IO: chat / tokens / metrics / logs / speak
   ▼
 Flask + Socket.IO server  (carnival/server.py)
   ├─ Agent (carnival/core/agent.py)
   │    ├─ GeminiClient (carnival/core/llm.py) ── Google Gemini API
   │    └─ Tool registry  ← built-in skills + user skills (function calling)
   ├─ Ctx  ── log / say / emit / memory / config / tts
   ├─ Memory (carnival/memory)  ← carnival/data/memory.json
   ├─ Dashboard metrics (carnival/dashboard)  ← psutil/NVML
   └─ TTS (browser by default; edge / pyttsx3 optional)
```

The conversation loop: user text → Gemini (with tool declarations) → if Gemini
emits function calls, the matching skill runs locally and the result is fed back
→ repeat until Gemini returns a spoken answer → streamed to the UI.

---

## 5. Project structure

```
C.A.R.N.I.V.A.L/
├── main.py                     # entry point (web / --text / --voice / --check / --skills)
├── start.sh                    # venv bootstrap + launcher
├── requirements.txt            requirements-dev.txt
├── .env.example
├── README.md  ATTRIBUTION.md  LICENSE
├── tests/                      # pytest suite (agent loop, skills, server, config)
│   ├── conftest.py  test_agent_loop.py  test_config.py
│   ├── test_plugin_loader.py  test_skills.py  test_server.py
└── carnival/
    ├── __init__.py             # version
    ├── server.py               # Flask + Socket.IO + chat persistence + REST API
    ├── core/
    │   ├── config.py           # settings + GEMINI_API_KEY (env-first)
    │   ├── log.py              # fan-out logger
    │   ├── llm.py              # Gemini client: streaming + backoff + tool schema
    │   ├── agent.py            # conversation loop + tool registry + system prompt
    │   ├── context.py          # Ctx passed to skills
    │   ├── plugin_loader.py    # skill discovery / validation / collision check
    │   ├── tts.py              # browser / edge-tts / pyttsx3
    │   └── stt.py              # optional headless mic (google / whisper)
    ├── memory/memory.py        # persistent JSON memory
    ├── dashboard/metrics.py    # CPU/RAM/disk/temp/GPU/battery/network + alerts
    ├── skills/                 # one file = one Gemini tool
    │   ├── system_status.py  sys_info.py  processes.py  media_control.py
    │   ├── screenshot.py  clipboard.py  daily_briefing.py
    │   ├── web_search.py  weather.py  reminder.py  open_app.py  file_ops.py
    │   ├── youtube.py  notes.py  music.py  smart_home.py  wikipedia.py
    │   ├── translate.py  time_date.py  calculator.py
    │   └── system_command.py   # (shell off by default)
    ├── data/                   # runtime: settings.json, memory.json,
    │   └── skills/_template.py # reminders.json, chat_history.json, user skills
    └── ui/
        ├── templates/index.html
        └── static/css/styles.css  static/js/app.js
```

### REST API (in addition to the Socket.IO events)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Liveness + configured state + skill count |
| `/api/version` | GET | Version info |
| `/api/metrics` | GET | One-shot system metrics snapshot |
| `/api/config` | GET/POST | Read / update settings (model change hot-rebuilds) |
| `/api/skills` | GET | Discovered skills with enabled/broken flags |
| `/api/history` | GET/DELETE | Restore or clear persisted conversation |

---

## 6. Writing a new skill

Create `carnival/data/skills/my_skill.py`:

```python
SKILL = {
    "name": "my_skill",
    "description": "When the user asks X, call this. Be explicit about triggers.",
    "parameters": {"type": "OBJECT",
                   "properties": {"q": {"type": "STRING", "description": "..."}},
                   "required": ["q"]},
}

def run(parameters: dict, ctx=None) -> str:
    return f"Result for {parameters.get('q')}"
```

Restart C.A.R.N.I.V.A.L. It is auto-discovered, registered as a Gemini tool, and
listed in the dashboard. Invalid/duplicate skills are isolated (shown as BROKEN)
and never crash the assistant.

---

## 7. Edge cases handled

- **No API key** → UI shows a clear "not configured" message; server still loads.
- **No microphone / unsupported browser** → mic button disabled; text still works.
- **Gemini 429 / 5xx / timeout** → exponential backoff, then a graceful fallback reply.
- **Offline** → browser TTS + cached skills; web/weather skills degrade with messages.
- **Permission denied / missing module** → skills catch their own errors and return
  a spoken message instead of raising.
- **Server restart mid-conversation** → chat history is restored from
  `carnival/data/chat_history.json`; pending reminders are re-armed automatically.
- **Broken user skill** → rejected at scan time, logged, never crashes the agent.
- **History growth** → conversation context is trimmed at safe boundaries so
  tool-call pairs are never split.

---

## 8. Attribution & licenses

C.A.R.N.I.V.A.L is a derivative work built primarily on **Mark-LI-main** and
incorporating ideas from several other open-source assistants. See
`ATTRIBUTION.md` for the full list and license terms. The package is distributed
under **CC BY-NC 4.0** (inherited from the Mark-LI base). The original downloaded
repositories were **not modified or deleted**.
