#!/usr/bin/env python3
"""C.A.R.N.I.V.A.L — entry point.

Modes
-----
  python main.py                 Launch the web dashboard at http://127.0.0.1:8000
  python main.py --text         Run a terminal chat loop (great for testing)
  python main.py --voice        Headless voice mode (mic in, TTS out)
  python main.py --check        Self-test: deps, config, skills, agent loop
  python main.py --skills       List discovered skills and exit
  python main.py --version      Print version
  python main.py --host 0.0.0.0 --port 9000   Bind on all interfaces

The Gemini API key MUST come from the GEMINI_API_KEY environment variable
(or your .env file). Never commit a real key.
"""
from __future__ import annotations

import argparse
import importlib
import sys

import carnival
from carnival.core.config import Config
from carnival.core.context import Ctx
from carnival.core.log import info, error, warn


def _build_agent(config: Config):
    if not config.is_configured:
        error("GEMINI_API_KEY is not set. Export it or add it to .env, then retry.")
        sys.exit(2)
    try:
        from carnival.core.llm import GeminiClient
        from carnival.core.agent import Agent
        from carnival.core.tts import create_player
        client = GeminiClient(config.gemini_api_key, config.gemini_model,
                              config.temperature, config.max_output_tokens)
        tts = create_player(config)
        return Agent(client, config, tts=tts), tts
    except Exception as e:
        error(f"Failed to start C.A.R.N.I.V.A.L: {e}")
        sys.exit(2)


def run_web(config: Config, host: str, port: int) -> None:
    from carnival.server import run as run_server
    run_server(host=host, port=port)


def run_text(config: Config) -> None:
    agent, tts = _build_agent(config)
    ctx = Ctx(log=info, say=lambda t: None, config=config, tts=tts)
    print(f"\n{config.assistant_name} ready. Type 'exit' to quit.\n")
    while True:
        try:
            text = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not text:
            continue
        if text.lower() in ("exit", "quit"):
            break
        final = agent.turn(text, ctx, on_token=lambda t: print(t, end="", flush=True))
        print("\n" + final + "\n")


def run_voice(config: Config) -> None:
    agent, tts = _build_agent(config)
    from carnival.core.stt import MicrophoneListener

    ctx = Ctx(log=info, say=tts.speak, config=config, tts=tts)

    def handle(text: str):
        if not text:
            return
        print(f"\nYou: {text}")
        final = agent.turn(text, ctx, on_token=lambda t: None)
        print(f"{config.assistant_name}: {final}")
        tts.speak(final)

    info("Voice mode: speak after the prompt. Ctrl-C to stop.")
    lis = MicrophoneListener(config.stt_engine if config.stt_engine != "browser" else "google")
    lis.start(handle)
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        lis.stop()
        print("\nGoodbye.")


def run_check(config: Config) -> int:
    """Self-test: dependencies, config, skills, agent loop. Exit code 0 = healthy."""
    print(f"C.A.R.N.I.V.A.L v{carnival.__version__} — self-test\n" + "=" * 46)
    failures = 0

    def check(label: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{mark}] {label}" + (f" — {detail}" if detail else ""))

    # 1) core deps
    for mod in ("flask", "flask_socketio", "google.genai", "psutil", "dotenv"):
        try:
            importlib.import_module(mod)
            check(f"dependency {mod}", True)
        except ImportError as e:
            check(f"dependency {mod}", False, str(e))

    # 2) config
    check("GEMINI_API_KEY configured", config.is_configured,
          "set it in .env or environment" if not config.is_configured else "")
    check("model", True, config.gemini_model)

    # 3) skills discover + execute safely
    from carnival.core.plugin_loader import scan_skill_dir
    from carnival.core.agent import BUILTIN_SKILLS_DIR, USER_SKILLS_DIR, Agent  # noqa: F401
    records = list(scan_skill_dir(BUILTIN_SKILLS_DIR, set(), info).values())
    check("built-in skills discovered", len(records) >= 15, f"{len(records)} found")
    broken = [r.name for r in records if not r.valid]
    check("no broken skills", not broken, ", ".join(broken))
    ran_ok = 0
    for r in records:
        if not r.valid:
            continue
        try:
            out = r.run({}, None)
            if isinstance(out, str):
                ran_ok += 1
        except Exception:
            pass
    check("skills execute with empty args", ran_ok == len([r for r in records if r.valid]),
          f"{ran_ok} ok")

    # 4) agent loop with a scripted mock client (no network needed)
    class _Chunk:
        def __init__(self, text="", fcalls=None):
            self._t, self.fc = text, fcalls
        @property
        def text(self): return self._t
        @property
        def function_calls(self): return self.fc

    class _MockClient:
        def __init__(self):
            self.script = [("All systems nominal.", None)]
        def generate(self, contents, function_declarations=None,
                     system_instruction=None, on_token=None):
            return self.script.pop(0)

    try:
        agent = Agent(_MockClient(), config)
        out = agent.turn("ping", Ctx(log=lambda m: None, say=lambda t: None,
                                     emit=lambda e, d: None,
                                     memory=None, config=config, tts=None))
        check("agent loop (mock)", isinstance(out, str) and len(out) > 0, out[:40])
    except Exception as e:
        check("agent loop (mock)", False, f"{type(e).__name__}: {e}")

    # 5) server import sanity
    try:
        importlib.import_module("carnival.server")
        check("server module imports", True)
    except Exception as e:
        check("server module imports", False, str(e))

    print("=" * 46)
    if failures:
        print(f"{failures} check(s) FAILED.")
        return 1
    print("All checks passed. Ready to launch: python main.py")
    return 0


def list_skills(config: Config) -> int:
    from carnival.core.plugin_loader import scan_skill_dir
    from carnival.core.agent import BUILTIN_SKILLS_DIR, USER_SKILLS_DIR
    rows = []
    for label, d in (("builtin", BUILTIN_SKILLS_DIR), ("user", USER_SKILLS_DIR)):
        for r in scan_skill_dir(d, set(), info).values():
            enabled = config.module_enabled(r.name)
            rows.append((label, r.name, r.valid, enabled, r.error or ""))
    print(f"{'SRC':<8} {'NAME':<16} {'VALID':<6} ENABLED  NOTE")
    for src, name, valid, en, err in sorted(rows, key=lambda x: x[1]):
        print(f"{src:<8} {name:<16} {str(valid):<6} {str(en):<8} {err}")
    print(f"\n{len(rows)} skill file(s). Drop your own into "
          f"carnival/data/skills/ — see _template.py.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="C.A.R.N.I.V.A.L personal AI assistant")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--text", action="store_true", help="Terminal chat loop")
    ap.add_argument("--voice", action="store_true", help="Headless voice mode")
    ap.add_argument("--check", action="store_true", help="Run self-test and exit")
    ap.add_argument("--skills", action="store_true", help="List skills and exit")
    ap.add_argument("--version", action="store_true", help="Print version and exit")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    if args.version:
        print(f"C.A.R.N.I.V.A.L v{carnival.__version__}")
        return

    config = Config.load()
    if args.check:
        sys.exit(run_check(config))
    if args.skills:
        sys.exit(list_skills(config))
    if args.voice:
        run_voice(config)
    elif args.text:
        run_text(config)
    else:
        run_web(config, args.host, args.port)


if __name__ == "__main__":
    main()
