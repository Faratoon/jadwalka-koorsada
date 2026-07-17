"""
Helper: Telegram webhook si fudud u dir.
Tallaabooyinka:
  1. Bot deploy Vercel
  2. Soo qabo URL-ga (tusaale: https://macallin-bot.vercel.app)
  3. Shid: python set_webhook.py
"""
import requests
import os

TOKEN = os.environ.get("BOT_TOKEN", input("Geli TOKEN-kaaga: ").strip())
URL = input("Geli Vercel URL-gaaga (https://...): ").strip().rstrip("/")

WEBHOOK_URL = f"{URL}/webhook"

print(f"\nSetting webhook to: {WEBHOOK_URL}")

resp = requests.get(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    params={"url": WEBHOOK_URL}
)

data = resp.json()
if data.get("ok"):
    print("✅ Webhook waa la set gareeyay!")
    print(f"   URL: {WEBHOOK_URL}")
else:
    print(f"❌ Khalad: {data.get('description', 'Unknown')}")

# Hubi hadda
print("\nHubinta hadda...")
info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo").json()
print(f"   URL: {info['result'].get('url', 'None')}")
print(f"   Pending updates: {info['result'].get('pending_update_count', 0)}")
