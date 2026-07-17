"""
MACALLIN BOT - LOCAL TEST MODE (Polling)
Habka ugu fudud ee tijaabinta. Webhook ma loo baahanahay.
"""
import os
import sys
import signal
import asyncio
from pathlib import Path

# Load .env.local haddii jiro
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env.local"
    if env_file.exists():
        load_dotenv(env_file)
        print("[OK] Loaded .env.local")
    else:
        print("[WARN] .env.local ma jiro. Environment variables isticmaali.")
except ImportError:
    pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.bot_app import build_application
from telegram import Update

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
    print("  MACALLIN BOT - LOCAL POLLING MODE")
    print("=" * 60)
    print(f"  Token prefix: {token.split(':')[0]}")
    print(f"  Admin IDs: {os.environ.get('ADMIN_IDS', 'None')}")
    print("  Bot waa la shidlaya...")
    print("  Riix Ctrl+C si aad u joojiso.\n")

    async def run_bot():
        app = build_application()
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        print("[OK] Polling started! Telegram-ka /start riix.")

        # Run forever until Ctrl+C
        stop_event = asyncio.Event()
        def shutdown():
            print("\n[OK] Shutdown signal received...")
            stop_event.set()

        # Handle Ctrl+C on Windows
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, lambda s, f: shutdown())
        except Exception:
            pass

        await stop_event.wait()

        print("[OK] Stopping bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("[OK] Bot stopped. Nabad galyo!")

    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
