"""
MACALLIN BOT - Vercel Serverless Webhook Handler v3
Pattern: PTB v20+ async context manager (initialize/start/stop/shutdown automatic)
"""
import os
import sys
import json
import asyncio
import traceback
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Ku qor import error-ka haddii jiro — si diagnostics u noqdo
try:
    from telegram import Update
    from core.bot_app import build_application
    _IMPORT_OK = True
except Exception as _import_err:
    _IMPORT_OK = False
    _IMPORT_TRACE = traceback.format_exc()

# Token-ka environment-ka ka helo
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = os.environ.get("ADMIN_IDS", "")

class handler(BaseHTTPRequestHandler):
    def _json(self, status, data):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        """Health check + diagnostics"""
        diag = {
            "status": "ok",
            "import_ok": _IMPORT_OK,
            "token_set": bool(BOT_TOKEN and ":" in BOT_TOKEN),
            "token_prefix": BOT_TOKEN.split(":")[0] if ":" in BOT_TOKEN else "missing",
            "admin_ids": ADMIN_IDS,
        }
        if not _IMPORT_OK:
            diag["import_error"] = str(_import_err)
            diag["import_trace"] = _IMPORT_TRACE
        self._json(200, diag)

    def do_POST(self):
        """Process Telegram webhook update"""
        # 1. Body ka akhri
        try:
            clen = int(self.headers.get("Content-Length", 0))
            if clen == 0:
                self._json(400, {"error": "empty body"})
                return
            body = json.loads(self.rfile.read(clen).decode("utf-8"))
        except Exception:
            self._json(400, {"error": "bad json"})
            return

        # 2. Hubi imports
        if not _IMPORT_OK:
            self._json(500, {"error": "import failed", "detail": str(_import_err)})
            return

        # 3. Hubi token
        if not BOT_TOKEN:
            self._json(500, {"error": "BOT_TOKEN env var missing"})
            return

        # 4. Process gudaha async function
        async def _run():
            app = None
            try:
                app = build_application()
                # PTB v20+ context manager: waxa dhammaystira initialize/start/stop/shutdown
                async with app:
                    update = Update.de_json(body, app.bot)
                    await app.process_update(update)
                return {"ok": True}
            except Exception:
                trace = traceback.format_exc()
                # Isku day inaad shutdown haddii app la bilaabay
                if app:
                    try:
                        await app.stop()
                        await app.shutdown()
                    except Exception:
                        pass
                return {"ok": False, "error": trace}

        # 5. Run asyncio
        try:
            result = asyncio.run(_run())
        except Exception:
            result = {"ok": False, "error": traceback.format_exc()}

        # 6. Hadmindha — Telegram waxay u baahan tahay 200 (kaliya xitaa qalad)
        self._json(200, result)
