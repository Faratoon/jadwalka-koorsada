# 🚀 DEPLOY NOW — Quick Steps

## YOU ARE HERE:
```
[✅ GitHub] → [✅ Vercel Import] → [🔴 YOU: Add ENV] → [🔴 Deploy] → [🔴 Webhook] → [✅ Done]
```

---

## 1. ADD ENVIRONMENT VARIABLES NOW

In the Vercel dashboard where you are now, look for:

**"Environment Variables"** section

Click **"Add"** and add these 2:

```
Key:   BOT_TOKEN
Value: <REDACTED_BOT_TOKEN>
```

```
Key:   ADMIN_IDS  
Value: 6340767923
```

---

## 2. CLICK "DEPLOY"

Wait 1-2 minutes.

---

## 3. GET YOUR URL

After deploy finishes, you will see something like:
```
https://jadwalka-koorsada.vercel.app
```

**Copy this URL!**

---

## 4. SET WEBHOOK

Open browser and paste this URL:
```
https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/setWebhook?url=https://jadwalka-koorsada.vercel.app/webhook
```

You should see:
```json
{"ok":true,"result":true}
```

---

## 5. TEST BOT

Open Telegram, message your bot:
```
/start
```

Bot should reply! 🎉

---

## 🔥 ONE-LINER WEBHOOK (Copy & Paste)

```bash
curl "https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/setWebhook?url=https://jadwalka-koorsada.vercel.app/webhook"
```

---

## ⚠️ IMPORTANT

**If your token was exposed before:**
- Go to @BotFather NOW
- Send: `/revoke`
- Get NEW token
- Update Vercel Environment Variable with new token
- Update webhook URL with new token

---

## 🎯 DONE!

Your bot is live at:
- 🌐 https://jadwalka-koorsada.vercel.app
- 🤖 t.me/YourBotUsername

Hambalyo! 🎓
