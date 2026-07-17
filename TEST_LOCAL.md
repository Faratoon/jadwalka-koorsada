# 🧪 TIJAABO LOCAL — Sida Loo Shido Computer-kaaga

Waxaad hadda u baahan tahay inaad **tijaabiso** bot-ka kahor intaadan Vercel deploy-gareyn.

---

## 🔴 HABKA 1: POLLING MODE (Ugu Fudud — 2 Tallaabo)

### Tallaabo 1: `.env.local` Samee
Fur folder-ka `teacher_schedule`, samee fayl cusub:

**Magaca faylka:** `.env.local`

**Qaybta ku qor:**
```env
BOT_TOKEN=<REDACTED_BOT_TOKEN>
ADMIN_IDS=6340767923
```

**⚠️ OGAYSII:** Faylkan waa `.gitignore` — ma push-gareyn doono GitHub.

---

### Tallaabo 2: Shid Bot-ka
Fur **Command Prompt** ama **PowerShell**, ku qor:

```bash
cd "C:\Users\Farat\teacher_schedule"
python run_local.py
```

Waxaad arki doontaa:
```
============================================================
  🤖 MACALLIN BOT - LOCAL POLLING MODE
============================================================
  Token prefix: 6340767923
  Admin IDs: 6340767923
  Bot waa la shidlaya...
  Riix Ctrl+C si aad u joojiso.
```

---

### Tallaabo 3: Tijaabo Telegram-ka
Fur Telegram, message bot-kaaga:
```
/start
```

**Waa inuu jawaabayaa!** 🎉

---

### Tallaabo 4: Jooji
Computer-ka riix **Ctrl+C** si aad u joojiso.

---

## 🟢 HABKA 2: WEBHOOK + ngrok (Haddii aad rabto)

Haddii aad rabto inaad **webhook-ga Vercel-ka ah** tijaabiso kahor deploy:

### 1. ngrok soo dajiso
Aadi: https://ngrok.com/download

### 2. ngrok shid
```bash
ngrok http 8000
```

Waxaad arki doontaa URL sida:
```
https://a1b2c3d4.ngrok.io
```

### 3. Webhook set
```
https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/setWebhook?url=https://a1b2c3d4.ngrok.io
```

### 4. Server local shid
```bash
cd "C:\Users\Farat\teacher_schedule"
python run_webhook_local.py
```

---

## 📋 Hubinta (Checklist)

| Waxa la hubiyo | Soo koobid |
|---------------|-----------|
| python --version | 3.10+ waa inuu yahay |
| pip list | python-telegram-bot, fpdf2, Pillow, qrcode |
| .env.local | BOT_TOKEN + ADMIN_IDS ku qoran |
| /start Telegram | Bot wuu jawaabayaa? |
| /week | Casharada muuqda? |
| /progress | Progress bar muuqda? |

---

## 🆘 Common Errors

### "BOT_TOKEN ma jiro!"
**Sabab:** `.env.local` ma jiro ama TOKEN ma qoran.
**Xal:** `.env.local` samee, ku qor TOKEN.

### "Module not found"
**Sabab:** Packages lama shubin.
**Xal:**
```bash
pip install python-telegram-bot fpdf2 Pillow qrcode python-dotenv
```

### "Conflict: another bot is running"
**Sabab:** Bot-ku webhook-ka Vercel ayaa la set gareeyay. Polling iyo webhook ma shaqeeyaan isla waqtiga.
**Xal:**
```
https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/deleteWebhook
```

---

## ✅ Haddii wuu shaqeynayo

Haddii `/start` jawaabay:
- Bot-ku waa sax ✅
- Vercel-ka ayaa kaliya u baahan deploy

---

**Hadda samee:**
1. ✅ `.env.local` samee
2. ✅ `python run_local.py`
3. ✅ Telegram-ka `/start` riix

Bot-ku wuu shaqeynayaa? 🎉
