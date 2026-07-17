"""
MACALLIN BOT - Vercel Webhook Handler
Waxaa loo isticmaalaa Vercel Serverless Functions
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from telegram import Update
from core.bot_app import build_application

# Singleton Application (initialize once, reuse for each request)
_application = None

def get_app():
    global _application
    if _application is None:
        _application = build_application()
        asyncio.get_event_loop().run_until_complete(_application.initialize())
    return _application

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"MACALLIN BOT is running! Use POST /webhook for Telegram updates.")

    def do_POST(self):
        """Process Telegram webhook updates"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            return

        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        app = get_app()
        update = Update.de_json(data, app.bot)

        # Process update asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app.process_update(update))
        finally:
            loop.close()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
