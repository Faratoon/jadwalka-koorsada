# 🔥 FIREBASE SETUP — HABKA UGU FUDUD

Waxaan kuu soo koobay **5 tallaabo** si aad u xidhasho Firebase. Kaliya midkood isticmaal.

---

## 🎯 HABKA 1: JSON Credentials (Ugu Secure — Recommended)

### Tallaabo 1: Firebase Console Aadi
- Aadi: **https://console.firebase.google.com/**
- Samee **Project cusub** ama dooro kan hore

### Tallaabo 2: Project Settings Furan
- Console-ka midig taag, riix **⚙️ Settings (Gear icon)**
- Dooro **"Project settings"**

### Tallaabo 3: Service Accounts
- Tabs-ka ku meel gaar ah dooro **"Service accounts"**
- Riix button-ka **"Generate new private key"**
- Kalsooni ku qabo **"Generate key"**

### Tallaabo 4: JSON Soo Dajiso
- Fayl **JSON** ah ayaa computer-kaaga soo degaya (magaciisu waa sida `project-xxx-firebase-adminsdk-yyy.json`)
- **Soo koobi faylkaan**
- Ku geli folder-ka: `C:\Users\Farat\teacher_schedule\`
- **Magaca beddel:** `firebase-credentials.json`

### Tallaabo 5: Bot-ka Update Garee
```python
# telegram_course_bot_v2.py — line 35
FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"
```
Haddii ay horey u jirtay, iska daa — waa la qoray! Kaliya hubi in faylku ku yaalo folder-ka.

---

## 🌐 HABKA 2: Web Config (Haddii JSON aan kuu soo dhicin)

### Tallaabo 1: Firebase Console → Settings → General

### Tallaabo 2: "Your apps" → Riix `</>` (Web)

### Tallaabo 3: Config-ka soo qado oo ku qor bot-ka

```python
# telegram_course_bot_v2.py — line 44
FIREBASE_WEB_CONFIG = {
    "apiKey": "AIzaSyAbc123...",
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project-id",
    "databaseURL": "https://your-project-default-rtdb.firebaseio.com"
}
```

**Note:** Habkan wuxuu u baahan yahay inaad **Realtime Database** furato Firebase Console-ka.

---

## ✅ Hubinta (Verification)

Kadib markaad sameyso, shid bot-ka oo fiiri console-ka:

```bash
python telegram_course_bot_v2.py
```

Haddii Firebase si sax ah ugu xidhan tahay, waxaad arki doontaa:
```
✅ Firebase connected! Xogta waa clouds-ka.
```

Haddii kale:
```
📁 Firebase ma diyaar ah. Local JSON mode: students.json
```

Waa inoo og yahay — bot-ku wuu shaqeyn doonaa labadaba!

---

## 🔧 Common Errors

| Error | Sabab | Xalka |
|-------|-------|-------|
| `Failed to initialize certificate` | JSON file ma habboona | Hubi in faylku yahay `firebase-credentials.json` oo ku yaal folder-ka bot-ka |
| `Permission denied` | Firestore rules ma furan | Firebase Console → Firestore Database → Rules: `allow read, write: if true;` (development) |
| `firebase-admin ma jiro` | Package lama shubin | `pip install firebase-admin` |

---

## 🚀 Dhaqan Gelin (One-liner Test)

Haddii aad rabto inaad si dhakhso ah u hubiso xidhiidhka:

```bash
cd teacher_schedule
python -c "from firebase_setup import check_firebase_ready; check_firebase_ready()"
```

---

**Waa dhamaad!** Haddii aad weli welwel qabto, ii soo dir screenshot-ka ama qoraalka error-ka. 🎯
