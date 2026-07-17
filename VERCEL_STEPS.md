# 🚀 VERCEL DEPLOYMENT — Tallaabooyinka Hara

## ✅ Hadda La Sameeyay
- [x] GitHub repo: `jadwalka-koorsada`
- [x] Import Vercel → `Tijaabo2` Hobby
- [x] Framework: Python
- [x] Root: `./`

---

## 🔴 TALLAABO 1: ENVIRONMENT VARIABLES (MUHIIM!)

Waxaad hadda arki doontaa "Environment Variables" ama waxaad ku dari kartaa Settings-ka kadib.

Ku dar labadaan:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `<REDACTED_BOT_TOKEN>` |
| `ADMIN_IDS` | `6340767923` |

### Sida loo ku daro:
1. Haddii hadda aragtid "Environment Variables":
   - Key: `BOT_TOKEN`
   - Value: `<REDACTED_BOT_TOKEN>`
   - Riix **Add**
   - Key: `ADMIN_IDS`
   - Value: `6340767923`
   - Riix **Add**

2. Haddii aan la muuqan:
   - Settings → Environment Variables
   - Ku dar halkaas

---

## 🔴 TALLAABO 2: DEPLOY

Riix **DEPLOY** button-ka!

Waxaad arki doontaa:
```
Building...
```

Waxay qaadataa 30 seconds - 2 minutes.

---

## 🔴 TALLAABO 3: URL-GAAGA HEL

Kadib marka deploy uu dhammaystiro, waxaad heli doontaa:

```
https://jadwalka-koorsada.vercel.app
```

**Soo qado URL-kaan!**

---

## 🔴 TALLAABO 4: WEBHOOK SET GAREE

### A. Browser (Ugu fudud)
Fur browser-kaaga, ku qor:
```
https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/setWebhook?url=https://jadwalka-koorsada.vercel.app/webhook
```

Waa inaad aragtaa:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### B. Command Line
```bash
curl -X POST "https://api.telegram.org/bot<REDACTED_BOT_TOKEN>/setWebhook" \
  -d "url=https://jadwalka-koorsada.vercel.app/webhook"
```

---

## 🔴 TALLAABO 5: HUBI

### Health Check
Fur browser:
```
https://jadwalka-koorsada.vercel.app
```

Waa inaad aragtaa:
```
MACALLIN BOT is running! Use POST /webhook for Telegram updates.
```

### Bot Test
Telegram ku riix:
```
/start
```

Bot-ku waa inuu jawaabayaa! 🎉

---

## 🆘 HADDII KHALAAD

| Khalad | Xal |
|--------|-----|
| "Not Found" | Webhook URL ma set gareyn |
| "Unauthorized" | TOKEN waa khaldan ama revoke la sameeyay |
| "Build Error" | requirements.txt hubi |
| "Module not found" | Python version hubi (3.12+) |

---

## 🔗 Links-ka Ugu Muhiimsan

| Waxa | Link |
|------|------|
| Vercel Dashboard | https://vercel.com/dashboard |
| Project Settings | https://vercel.com/faratoon/jadwalka-koorsada/settings |
| Bot Health | https://jadwalka-koorsada.vercel.app |
| Telegram API | https://api.telegram.org |

---

**Waxaad hadda u baahan tahay kaliya:**
1. ✅ Environment Variables (BOT_TOKEN + ADMIN_IDS)
2. ✅ Riix DEPLOY
3. ✅ Set Webhook
4. ✅ Test /start

Hambalyo! 🚀
