# 🚀 MACALLIN BOT — Deploy Guide (GitHub + Vercel)

Waxaan kuu soo koobay **4 tallaabo** si aad u deploy-gareyso bot-kaada.

---

## 📋 TALAABADA 1: HEL TELEGRAM BOT TOKEN

### @BotFather
1. Telegram fur → Search **@BotFather**
2. Riix **START** → `/newbot`
3. Magac u bixi bot-ka (tusaale: `MacallinAIBot`)
4. Username u bixi (waa inuu dhammaadaa `bot`, tusaale: `macallin_ai_bot`)
5. **TOKEN** ayaa soo baxaya — qabo!

```
123456789:AAHgfhgfhgfhgf...  <-- TOKEN-kaaga
```

**⚠️ Ha qasin TOKEN-ka qofna!**

---

## 📋 TALAABADA 2: KU QOR TOKEN-KAAGA

### A. Haddii Local Tijaabiyo:
```bash
# Fur .env.example, u beddel .env
# Ku qor:
BOT_TOKEN=123456789:AAHxxxxYOUR_TOKEN_HERExxxx
ADMIN_IDS=123456789       # Qor Telegram ID-gaaga
```

### B. Vercel Environment Variables (Waa inaad halkaas ku qorto):
Vercel Dashboard → Project Settings → Environment Variables

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `123456789:AAHxxxx...` |
| `ADMIN_IDS` | `123456789` |

---

## 📋 TALAABADA 3: PUSH GITHUB

### 1. GitHub Repo Samee
- Aadi https://github.com/new
- Magac bixi (tusaale: `macallin-bot`)
- **Create repository**

### 2. Local Folder Link Garee
```bash
cd teacher_schedule

git init
git add .
git commit -m "Initial commit - MACALLIN BOT v2.0"

git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/macallin-bot.git
git push -u origin main
```

**Tayada files-ka ee GitHub:**
```
macallin-bot/
├── api/
│   └── webhook.py          # Vercel handler
├── core/
│   └── bot_app.py          # Logic-ga bot-ka
├── course_data.py          # 70 cashar
├── run_local.py            # Local test
├── requirements.txt
├── vercel.json
├── .env.example
└── README.md
```

---

## 📋 TALAABADA 4: DEPLOY VERCEL

### A. Vercel Account Samee
- Aadi https://vercel.com/signup
- Soo koobi GitHub account-kaaga

### B. New Project
1. Vercel Dashboard → **Add New Project**
2. Import Git Repository → Dooro `macallin-bot`
3. Framework Preset: **Other**
4. Environment Variables ku dar:
   - `BOT_TOKEN` = token-kaaga
   - `ADMIN_IDS` = ID-gaaga
5. **Deploy**

### C. Webhook Set Garee
Kadib marka deploy uu dhammaystiro, waxaad heli doontaa URL:

```
https://macallin-bot-xxx.vercel.app
```

Hadda webhook u dir Telegram API:

```bash
curl -F "url=https://macallin-bot-xxx.vercel.app/webhook" \
     https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook
```

Ama browser ku fur:
```
https://api.telegram.org/bot123456789:AAHxxxx/setWebhook?url=https://macallin-bot-xxx.vercel.app/webhook
```

**Haddii sax yahay, waxaad arki doontaa:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

---

## 🔧 HUBINTA (Verification)

### 1. Health Check
Browser ku fur:
```
https://macallin-bot-xxx.vercel.app
```
Waa inaad aragtaa: `MACALLIN BOT is running!`

### 2. Bot Test
Telegram ku riix `/start` → waa inuu jawaabayaa!

---

## 🔄 Update Soo Saar (Redeploy)

Marka aad wax badasho:
```bash
git add .
git commit -m "Update feature"
git push origin main
```
Vercel wuxuu si automatic ah ayuu redeploy u sameynayaa!

---

## 🆘 Common Problems

| Problem | Sabab | Xal |
|---------|-------|-----|
| "Bot not responding" | Webhook ma set | `/setWebhook` mar labaad ku celi |
| "Application Error" | Token ma qoran | Vercel env vars hubi |
| "Module not found" | requirements.txt ma jiro | Hubi in `requirements.txt` uu yahay GitHub |
| "Webhook timeout" | Cold start | Normal — Vercel free tier waa mid yaraanaya |

---

## 📞 Taageero

Haddii aad welwel qabto:
- Telegram: @YourUsername
- Email: your@email.com

---

**Deploy Ready!** 🚀
