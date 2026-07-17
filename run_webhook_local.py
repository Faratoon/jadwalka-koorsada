"""
MACALLIN BOT - LOCAL WEBHOOK TEST (ngrok)
========================================
Habka webhook-ga local aad u tijaabiso. Waa inaad:
  1. ngrok ku shub / soo dajiso: https://ngrok.com/download
  2. ./ngrok http 8000 (port-ka hoos ku qoran)
  3. Webhook URL-ga ngrok ku qor
  4. python run_webhook_local.py
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load .env.local
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env.local"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from telegram import Update
from core.bot_app import build_application

PORT = int(os.environ.get("PORT", 8000))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Nadiifi logs

    def do_POST(self):
        try:
            clen = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(clen).decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        async def process():
            app = build_application()
            async with app:
                update = Update.de_json(body, app.bot)
                await app.process_update(update)

        asyncio.run(process())

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Webhook server running. Use POST / for Telegram updates.")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("[ERROR] BOT_TOKEN ma jiro. .env.local hubi.")
        sys.exit(1)

    print("=" * 60)
    print("  🌐 LOCAL WEBHOOK SERVER")
    print("=" * 60)
    print(f"  Listening on http://127.0.0.1:{PORT}/")
    print("\n  Tallaabooyinka ngrok:")
    print(f"    1. Fur terminal cusub")
    print(f"    2. ngrok http {PORT}")
    print(f"    3. Webhook set:")
    print(f"       https://api.telegram.org/bot{BOT_TOKEN.split(':')[0]}:.../setWebhook?url=https://YOUR_NGROK.ngrok.io")
    print("\n  Riix Ctrl+C si aad u joojiso.\n")

    server = HTTPServer(("127.0.0.1", PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Server waa la joojiyay.")
