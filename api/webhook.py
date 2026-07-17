"""
MACALLIN BOT - Vercel Serverless Webhook Handler v5
BaseHTTPRequestHandler + Ultra defensive error handling
Always returns 200 to Telegram to prevent retry loops.
"""
import os
import sys
import json
import traceback
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add project root
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Quiet

    def _json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Health check"""
        token = os.environ.get("BOT_TOKEN", "")
        self._json(200, {
            "ok": True,
            "status": "running",
            "token_present": bool(token),
            "token_prefix": token.split(":")[0] if ":" in token else "none",
            "admin_ids": os.environ.get("ADMIN_IDS", "")
        })

    def do_POST(self):
        """Process Telegram update - NEVER crash, ALWAYS return 200"""
        # Step 1: Read body safely
        try:
            clen = int(self.headers.get("Content-Length", 0))
            if clen == 0:
                self._json(200, {"ok": True, "note": "empty"})
                return
            post_data = self.rfile.read(clen)
            body = json.loads(post_data.decode("utf-8"))
        except Exception as e:
            self._json(200, {"ok": True, "note": f"read_error: {str(e)}"})
            return

        # Step 2: Process with lazy import
        try:
            import asyncio
            from telegram import Update
            from core.bot_app import build_application

            token = os.environ.get("BOT_TOKEN", "")
            if not token:
                self._json(200, {"ok": True, "note": "no_token"})
                return

            async def _run():
                app = None
                try:
                    app = build_application()
                    await app.initialize()
                    await app.start()
                    update = Update.de_json(body, app.bot)
                    await app.process_update(update)
                    return {"ok": True, "processed": True}
                except Exception as inner:
                    return {"ok": True, "error": str(inner), "trace": traceback.format_exc()}
                finally:
                    if app:
                        try:
                            await app.stop()
                            await app.shutdown()
                        except:
                            pass

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_run())
            finally:
                loop.close()

            self._json(200, result)

        except Exception as outer:
            # Absolute last resort - still return 200
            print(f"WEBHOOK CRASH: {str(outer)}")
            print(traceback.format_exc())
            self._json(200, {"ok": True, "note": "handler_crashed", "error": str(outer)})
