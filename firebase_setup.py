"""
=============================================================
FIREBASE SETUP — MACALLIN BOT (Habka Fudud)
=============================================================
Labadan hab ee hoos ku qoran midkood isticmaal:

HAB 1: JSON Credentials File (Ugu Secure)
HAB 2: Firebase Console Direct (Ugu Fudud — Waxaan kuu soo koobay)

=============================================================
"""

import os
from pathlib import Path

# ============== HAB 1: JSON CREDENTIALS FILE ==============
"""
Tallaabooyinka:
    1. Aadi https://console.firebase.google.com/
    2. Samee Project cusub (ama dooro kan hore)
    3. Settings (gear icon) → Project Settings
    4. Service Accounts tab
    5. "Generate new private key"
    6. JSON file ayaa soo degaya — magaca beddel: firebase-credentials.json
    7. Soo koobi faylka, ku qor meeshaan: teacher_schedule/

Markaas beddel:
    FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"
"""
FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"  # Halkan beddel

# ============== HAB 2: FIREBASE CONFIG (WEB/API) ==============
"""
Tallaabooyinka (Ugu Fudud):
    1. Firebase Console → Project Settings → General
    2. Hoose ku qoran "Your apps" → Add app (Web)</> 
    3. Qado config-kaan oo ku qor hoos:
"""

FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY_HERE",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID",
    "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com"
}

# ============== DHAQAN GELINTA ==============
def get_firebase_creds_path():
    """Hel path-ka credentials-ka"""
    local_path = Path(__file__).parent / FIREBASE_CREDENTIALS_PATH
    if local_path.exists():
        return str(local_path)
    if Path(FIREBASE_CREDENTIALS_PATH).exists():
        return FIREBASE_CREDENTIALS_PATH
    return None

def check_firebase_ready():
    """Hubi haddii Firebase diyaar yahay"""
    path = get_firebase_creds_path()
    if path:
        print(f"✅ Firebase credentials helay: {path}")
        return True, path
    
    # Check config-ka web-ka
    if FIREBASE_CONFIG.get("apiKey") and "YOUR" not in FIREBASE_CONFIG["apiKey"]:
        print("✅ Firebase Web config helay (Realtime Database mode)")
        return True, None
    
    print("⚠️ Firebase ma diyaar ah. Local JSON mode ayaa la isticmaali doonaa.")
    return False, None

if __name__ == "__main__":
    ready, path = check_firebase_ready()
    if ready:
        print("🚀 Firebase waa diyaar!")
        if path:
            print(f"   Path: {path}")
    else:
        print("📁 Local mode: students.json")
