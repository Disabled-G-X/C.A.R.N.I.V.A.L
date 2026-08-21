# Attribution & License Notes

C.A.R.N.I.V.A.L was produced by auditing and merging multiple open-source
J.A.R.V.I.S-style repositories found in `/home/obsycronite/Carnival - Data/`.
The original repositories were **read only** — none were modified or deleted.

## Base (primary foundation)
- **Mark-LI-main** — *The Ultimate Cross-Platform Personal AI Assistant*
  by FatihMakes. License: **Creative Commons BY-NC 4.0**.
  Reused as the architectural base: plugin/skill discovery + crash isolation
  pattern, the `PLUGIN`/`SKILL` single-file skill contract, `config_manager`
  opt-out enable model, long-term `memory.json` structure + prompt formatting,
  `system_monitor` (NVML/pynvml/psutil telemetry), `open_app` cross-platform
  launcher aliases, `file_controller` sandboxed file ops, `web_search` dual
  Gemini-grounded + DuckDuckGo fallback, `reminder` scheduling approach, and the
  `tts.py` engine factory (Edge/Kokoro/pyttsx3). These were re-implemented in a
  cleaner, Gemini-API-centric shape.

## Other models audited and ideas integrated
- **ada_v2-main** (MIT, Nazir Louis) — *A.D.A V2*. Inspired the **smart-home**
  skill (TP-Link Kasa via `python-kasa`) and the multi-modal/tool-use framing.
  `smart_home.py` mirrors its Kasa control concept.
- **barehands-main** (AGPL-3.0, jaredrhod) — *barehands*. Inspired the
  gesture/waveform "hands-on" UI philosophy; the web waveform visualiser and
  glassy animated aesthetic echo this. (Barehands code itself was not copied;
  AGPL would require source disclosure if integrated.)
- **fullstack-agent-main** (AGPL-3.0, jaredrhod) — *fullstack-agent*. Inspired the
  modular "mind + voice + face" separation and the `data/skills/` drop-in folder.
- **Jarvis-Desktop-Voice-Assistant-main** (MIT, Kishan Kumar Rai) — simple desktop
  voice assistant. Inspired the lightweight single-file skill ergonomics and the
  notes/screenshot conveniences folded into `notes.py`.
- **JARVIS-main** (MIT, Microsoft) — *HuggingGPT / easytool / taskbench*. Research
  codebase; informed the tool-calling/agent-loop design conceptually (no code reused).
- **Jarvis-master** (MIT, Sukeesh) — CLI assistant with `@plugin` decorator system.
  Inspired the clear plugin-object interface pattern used by `plugin_loader.py`.
- **JARVIS-master** (MIT, Atharva Ingle) — PyQt desktop assistant. Inspired the
  dashboard + HUD layout direction (reimplemented as a web dashboard).

## Licensing summary
| Project | License | Reused |
|---|---|---|
| Mark-LI-main | CC BY-NC 4.0 | Base architecture, skills, memory, TTS/STT patterns |
| ada_v2-main | MIT | Smart-home (Kasa) concept |
| barehands-main | AGPL-3.0 | UI/gesture philosophy (no code copied) |
| fullstack-agent-main | AGPL-3.0 | Modular layout idea (no code copied) |
| Jarvis-Desktop-Voice-Assistant-main | MIT | Skill ergonomics, notes |
| JARVIS-main | MIT | Tool-calling concept |
| Jarvis-master | MIT | Plugin interface pattern |
| JARVIS-master | MIT | Dashboard/HUD direction |

**Combined work license:** CC BY-NC 4.0 (inherited from the Mark-LI base), with
attribution to all projects above. The AGPL-licensed projects (barehands,
fullstack-agent) were used for *inspiration only*; no AGPL-covered source was
incorporated, so no source-disclosure obligation is triggered. All original
licenses and copyright notices are preserved in the source repositories.

> Note: CC BY-NC 4.0 is a **non-commercial** license. For commercial use you must
> obtain permission from the respective authors or re-implement the base without
> the CC BY-NC components.
