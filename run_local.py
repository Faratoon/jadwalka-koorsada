"""
MACALLIN BOT - LOCAL TEST MODE (Polling)
=====================================
Habka ugu fudud ee tijaabinta. Webhook ma loo baahanahay.
Waxaad u baahan tahay:
  1. .env.local file (TOKEN iyo ADMIN_IDS ku qoran)
  2. Riix: python run_local.py
"""
import os
import sys
import signal
from pathlib import Path

# Load .env.local haddii jiro
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env.local"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[OK] Loaded .env.local")
    else:
        print("[WARN] .env.local ma jiro. Environment variables isticmaali.")
except ImportError:
    pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.bot_app import build_application

def main():
    token = os.environ.get("BOT_TOKEN", "")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("\n[ERROR] BOT_TOKEN ma jiro!")
        print("        Fadlan .env.local samee ama environment variable set garee.\n")
        print("        Tusaale .env.local:")
        print("        BOT_TOKEN=6340767923:AAH...")
        print("        ADMIN_IDS=6340767923\n")
        sys.exit(1)

    print("=" * 60)
    print("  🤖 MACALLIN BOT - LOCAL POLLING MODE")
    print("=" * 60)
    print(f"  Token prefix: {token.split(':')[0]}")
    print(f"  Admin IDs: {os.environ.get('ADMIN_IDS', 'None')}")
    print("  Bot waa la shidlaya...")
    print("  Riix Ctrl+C si aad u joojiso.\n")

    app = build_application()

    def shutdown(signum, frame):
        print("\n[OK] Bot waa la joojiyay. Nabad galyo!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    # run_polling with drop_pending_updates si aad uga fogaato flood
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    from telegram import Update
    main()
