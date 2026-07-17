# 🤖 MACALLIN AI BOT v2.0 — Teacher Schedule + Automation

Waa nidaam dhammaystiran oo loogu talagalay dhexdhexaadinta koorsada 70-casharka ah.

---

## 🆕 Waxa Cusub v2.0

| Feature | Sharaxaad |
|---------|-----------|
| 🎯 **Quiz Automatic** | Bot-ku wuxuu waydiinayaa su'aalo ka dib cashar kasta. Score waa la xifdiyaa. |
| 📜 **Certificate PDF** | Marka 70/70 cashar la dhammaystiro, PDF caddayn oo qurxoon oo leh QR code自动生成 |
| 🔥 **Firebase Database** | Xogta waa lagu kaydiyaa clouds-ka (optional — local JSON waa fallback) |
| 📊 **Admin Stats** | Ardayda ugu horreeya, quiz scores, certificates issued |

---

## 📁 Faylasha

| Fayl | Ujeeddo |
|------|---------|
| `telegram_course_bot_v2.py` | **Bot dhammaystiran** (v2) |
| `course_data.py` | Xogta 4 koorsadood + schedule generator |
| `teacher_schedule.html` | Schedule qurxoon oo browser-ka furan kara |
| `teacher_schedule.csv` | Excel/CSV schedule |
| `requirements.txt` | Dependency-yada Python |
| `students.json` | Xogta ardayda (local) |
| `certificates/` | PDF certificates la kaydiyo |

---

## 🚀 Habka Shidaalka

### 1. Ku shub dependency-yada
```bash
pip install -r requirements.txt
```

### 2. Ku qor TOKEN-kaaga
```python
# telegram_course_bot_v2.py gudihiisa
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]  # Qor Telegram ID-gaaga
```

### 3. Shid Bot-ka
```bash
python telegram_course_bot_v2.py
```

---

## 🎯 Quiz Automatic

- Marka ardaygu dhammaystiro cashar, button cusub oo "🎯 Quiz" ayaa muuqanaya
- Bot-ku wuxuu waydiinayaa 2-3 su'aal oo ku saabsan casharka
- Jawaabaha saxda ah iyo khaladaadka waa la muujiyaa
- Score waa la xifdiyaa — ardaygu wuu arki karaa `/progress`

### Sida loo diyaariyo Quiz cusub:
```python
# telegram_course_bot_v2.py — line 97
QUIZ_DATA = {
    "course_1": {
        "Cashar Magaciisa": [
            {
                "q": "Su'aalka?",
                "options": ["A", "B", "C", "D"],
                "correct": 0  # Index-ka jawaabta saxda ah
            },
        ],
    }
}
```

---

## 📜 Certificate PDF

### Shuruudaha helista:
- Dhammaystir **70/70** cashar
- Riix `/certificate` ama button 📜 Certificate

### Waxa ku jira PDF-ga:
- Magaca ardayga
- Course name: "MACALLIN AI — 70 Cashar Course"
- Taariikhda dhammaystirka
- Certificate ID (unique)
- QR code (hubinta caddaynta)
- Design qurxoon (gold + dark theme)

---

## 🔥 Firebase Database (Optional)

Haddii aad rabto in xogta clouds-ka lagu kaydiyo:

### 1. Firebase Project samee:
- Aadi [Firebase Console](https://console.firebase.google.com/)
- Samee project cusub → Firestore Database

### 2. Service Account JSON soo dajiso:
- Project Settings → Service Accounts → Generate new private key
- Soo kaydi faylka JSON

### 3. Ku qor bot-ka:
```python
FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"
```

### 4. Ku shub firebase-admin:
```bash
pip install firebase-admin
```

**Haddaan la diiwaan gelin:** Bot-ku si automatic ah ayuu u isticmaali doonaa `students.json` (local)

---

## 📅 Schedule-ka 14 Usbuuc

| Usbuuc | Xilliga | Koorsada |
|--------|---------|----------|
| 1–8 | July–Sep | K1: 40 Cashar AI (YouTube) |
| 9–10 | Sep | K2: AI Video Editing (Loom) |
| 11–12 | Sep–Oct | K3: Dropshipping + Zendrop |
| 13–14 | Oct | K4: Resources + Community |

---

## 🤖 Amarrada Bot-ka

### Ardayda
| Amar | Waxa sameeya |
|------|--------------|
| `/start` | Diiwaangelin + Menu |
| `/week` | Casharada usbuuca hadda |
| `/schedule` | Arag 14 usbuuc |
| `/progress` | Horumarkaaga + Quiz scores |
| `/quiz` | Quiz menu |
| `/certificate` | Hesho PDF caddayn |
| `/next` | Usbuuca xiga |
| `/help` | Caawimaad |

### Admin-ka (Adiga kaliya)
| Amar | Waxa sameeya |
|------|--------------|
| `/broadcast Fariin` | U dir dhammaan ardayda |
| `/stats` | Tirakoob + leaderboard |

---

## ⚙️ Automation-ka

- **Xusuusin Usbuucii:** Isniinta 09:00 AM — bot-ku wuxuu dirayaa casharada cusub
- **Progress Tracking:** Marka cashar la dhammaystiro
- **Quiz Scoring:** Automatic grading + feedback
- **Certificate Auto-detect:** Marka 70/70 la gaaro, bot-ku wuxuu ogeysiinayaa

---

## 📞 Taageero

Haddii aad welwel qabto ama feature kale aad rabto:
- La xiriir @YourUsername
- Email: your@email.com

---

**Sameeye:** MACALLIN AI 🤖  
**Nooca:** python-telegram-bot + fpdf2 + firebase (optional)
