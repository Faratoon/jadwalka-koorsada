"""
MACALLIN BOT - Local Test (Polling Mode)
Tijaabi bot-kaada computer-kaaga kahor intaadan Vercel deploy-gareyn.
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.bot_app import build_application

if __name__ == "__main__":
    print("=" * 60)
    print("  MACALLIN BOT - LOCAL TEST MODE")
    print("=" * 60)
    print("  Bot waa la shidlaya...")
    print("  Riix Ctrl+C si aad u joojiso.\n")

    app = build_application()
    app.run_polling(allowed_updates="update")
