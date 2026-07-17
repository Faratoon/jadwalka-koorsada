"""
=============================================================
MACALLIN TELEGRAM BOT v2.0 — Automation Course Bot
=============================================================
Waxaa leh:
  ✅ Weekly schedule + progress tracking + auto-reminders
  ✅ QUIZ AUTOMATIC — su'aalo ka dib cashar kasta
  ✅ CERTIFICATE PDF — marka koorsada la dhammaystiro
  ✅ FIREBASE DATABASE — xogta clouds-ka (optional)

Dependencies:
    pip install python-telegram-bot fpdf2 pillow qrcode
    # Firebase haddii aad rabto:
    pip install firebase-admin

Habka isticmaalka:
    1. BotFather ka samee bot, qaado TOKEN
    2. Ku qor TOKEN-kaaga, ADMIN_IDS, iyo FIREBASE_CONFIG (optional)
    3. python telegram_course_bot_v2.py
=============================================================
"""

import logging
import json
import os
import io
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ============== OPTIONAL: FIREBASE ==============
# Si fudud oo dhakhso ah u qor halkan. Labada hab:
#   1. JSON file: FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"
#   2. Web Config: FIREBASE_CONFIG dict-ka ku qor (haddii aad isticmaasho REST API)
# Haddii labaduba madhan yihiin, local JSON ayaa la isticmaali doonaa.

FIREBASE_ENABLED = False
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_ENABLED = True
except ImportError:
    pass

# HABKA 1 (Ugu Secure): JSON Service Account
# Firebase Console → Project Settings → Service Accounts → Generate New Private Key
# Soo dajiso JSON, magaca beddel: firebase-credentials.json, ku dar folder-ka bot-ka
FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"  # ← Halkan beddel

# HABKA 2 (Ugu Fudud): Web Config
# Firebase Console → Project Settings → General → Your Apps → Web App
# Config-ka ku qor hoos (Optional — haddii REST API la isticmaalo)
FIREBASE_WEB_CONFIG = {
    # "apiKey": "YOUR_API_KEY",
    # "authDomain": "your-project.firebaseapp.com",
    # "projectId": "your-project-id",
    # "databaseURL": "https://your-project-default-rtdb.firebaseio.com"
}

# ============== PDF + QR ==============
from fpdf import FPDF
import qrcode

# ============== DEJIMAHA MUHIIMKA AH ==============
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]  # Qor Telegram ID-gaaga (@userinfobot)

DATA_FILE = Path(__file__).parent / "students.json"
CERTIFICATES_DIR = Path(__file__).parent / "certificates"
CERTIFICATES_DIR.mkdir(exist_ok=True)

from course_data import COURSES, LESSONS_PER_WEEK, generate_schedule

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== QUIZ DATA ==============
QUIZ_DATA = {
    "course_1": {
        "Chatbot Aasaaska": [
            {"q": "Chatbot waa maxay?", "options": ["Program computer ah", "Qof", "App mobile", "Website"], "correct": 0},
            {"q": "ManyChat waa maxay?", "options": ["Browser", "Chatbot builder", "Game", "OS"], "correct": 1},
        ],
        "Prompt Heer Sare": [
            {"q": "Prompt waa maxay?", "options": ["Sawir", "Amar qoraal ah AI", "Cod", "Video"], "correct": 1},
            {"q": "Sidee loogu jawaabo AI si sax ah?", "options": ["Si qasacadeed", "Si cad oo faahfaahsan", "Tusaale la'aan", "Luqad kale"], "correct": 1},
        ],
        "Telegram Bot A to Z": [
            {"q": "BotFather waa maxay?", "options": ["Bot Telegram ah", "Qof", "Website", "App"], "correct": 0},
            {"q": "Webhook waa maxay?", "options": ["Sawir", "Xiriir server-to-server", "Video", "Cod"], "correct": 1},
        ],
        "Linux Hordhac": [
            {"q": "Linux waa maxay?", "options": ["Operating System", "Browser", "Game", "Phone"], "correct": 0},
            {"q": "Terminal-ka Linux wuxuu ku shaqeeyaa?", "options": ["GUI", "Command line", "Touch", "Voice"], "correct": 1},
        ],
    },
    "course_2": {
        "InVideo Fundamentals": [
            {"q": "InVideo wuxuu samayn karaa?", "options": ["Text-to-Video", "Codka oo kaliya", "Sawir", "Email"], "correct": 0},
        ],
        "Pictory.ai Introduction": [
            {"q": "Pictory.ai wuxuu u adeegaa?", "options": ["Video editing automation", "Xisaab", "Bank", "Phone call"], "correct": 0},
        ],
    },
    "course_3": {
        "MAXAA KU DOORNAY ZENDROP": [
            {"q": "Zendrop waa maxay?", "options": ["Dropshipping tool", "Bank", "School", "Hospital"], "correct": 0},
        ],
        "AI Dropshipping Sida Hawsha u Fududeeyey": [
            {"q": "AI sida ugu weyn ee Dropshipping u fududeeyay?", "options": ["Automation", "Cunto", "Biyo", "Dayax"], "correct": 0},
        ],
    },
    "course_4": {
        "WhatsApp Group (Quiz & Support)": [
            {"q": "WhatsApp Group-ka koorsadu wuxuu bixiyaa?", "options": ["Quiz & Support", "Cunto", "Ciyaar", "Film"], "correct": 0},
        ],
    }
}

# Helper: heso quiz-ga lesson kasta
def get_quiz_for_lesson(lesson_title: str):
    for course_quizzes in QUIZ_DATA.values():
        if lesson_title in course_quizzes:
            return course_quizzes[lesson_title]
    return None

# ============== DATABASE (Local + Firebase) ==============
class Database:
    def __init__(self):
        self.firestore_db = None
        # Hubi haddii JSON file uu jiro (folder-ka bot-ka gudahiisa)
        creds_path = Path(__file__).parent / FIREBASE_CREDENTIALS_PATH
        if not creds_path.exists():
            creds_path = Path(FIREBASE_CREDENTIALS_PATH)

        if FIREBASE_ENABLED and creds_path.exists():
            try:
                cred = credentials.Certificate(str(creds_path))
                firebase_admin.initialize_app(cred)
                self.firestore_db = firestore.client()
                logger.info("✅ Firebase connected! Xogta waa clouds-ka.")
            except Exception as e:
                logger.warning(f"⚠️ Firebase failed: {e}. Local JSON mode.")
        else:
            logger.info("📁 Firebase ma diyaar ah. Local JSON mode: students.json")

    def load_students(self) -> Dict[str, Any]:
        if self.firestore_db:
            docs = self.firestore_db.collection("students").stream()
            return {doc.id: doc.to_dict() for doc in docs}
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_student(self, user_id: str, data: dict):
        if self.firestore_db:
            self.firestore_db.collection("students").document(user_id).set(data)
        else:
            students = self.load_students()
            students[user_id] = data
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(students, f, ensure_ascii=False, indent=2)

    def get_student(self, user_id: str) -> Optional[dict]:
        students = self.load_students()
        return students.get(str(user_id))

    def all_students(self) -> Dict[str, Any]:
        return self.load_students()

db = Database()

# ============== STUDENT FUNCTIONS ==============
def register_student(user_id, first_name, username=""):
    uid = str(user_id)
    existing = db.get_student(user_id)
    if existing:
        return False
    data = {
        "user_id": user_id,
        "first_name": first_name,
        "username": username,
        "joined": str(datetime.now().date()),
        "current_week": 1,
        "completed_lessons": [],
        "quiz_scores": {},  # {lesson_title: score%}
        "active": True,
        "reminders": True,
        "certificate_issued": False,
    }
    db.save_student(uid, data)
    return True

def update_progress(user_id, week=None, completed_lesson=None, quiz_score=None):
    uid = str(user_id)
    student = db.get_student(user_id)
    if not student:
        return
    if week is not None:
        student["current_week"] = week
    if completed_lesson is not None:
        if completed_lesson not in student.get("completed_lessons", []):
            student.setdefault("completed_lessons", []).append(completed_lesson)
    if quiz_score is not None:
        student.setdefault("quiz_scores", {})[quiz_score["lesson"]] = quiz_score["score"]
    db.save_student(uid, student)

# ============== PDF CERTIFICATE GENERATOR ==============
class CertificatePDF(FPDF):
    def header(self):
        self.set_fill_color(26, 26, 46)
        self.rect(0, 0, 297, 210, "F")

    def create_certificate(self, name: str, course: str, date: str, cert_id: str):
        self.add_page("L", "A4")
        self.set_auto_page_break(False)

        # Border gold
        self.set_draw_color(255, 215, 0)
        self.set_line_width(3)
        self.rect(10, 10, 277, 190)
        self.set_line_width(1)
        self.rect(15, 15, 267, 180)

        # Title
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(255, 215, 0)
        self.set_y(35)
        self.cell(0, 20, "MACALLIN AI", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 18)
        self.set_text_color(200, 200, 200)
        self.cell(0, 12, "CERTIFICATE OF COMPLETION", align="C", new_x="LMARGIN", new_y="NEXT")

        # Line
        self.set_draw_color(255, 215, 0)
        self.line(80, 75, 217, 75)

        # Presented to
        self.set_y(90)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, "This certificate is proudly presented to", align="C", new_x="LMARGIN", new_y="NEXT")

        # Name
        self.set_y(105)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, name, align="C", new_x="LMARGIN", new_y="NEXT")

        # Course
        self.set_y(130)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(200, 200, 200)
        self.cell(0, 10, f"For successfully completing the course:", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 212, 255)
        self.cell(0, 12, course, align="C", new_x="LMARGIN", new_y="NEXT")

        # Details
        self.set_y(160)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Date of Completion: {date}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 8, f"Certificate ID: {cert_id}", align="C", new_x="LMARGIN", new_y="NEXT")

        # QR
        qr_path = CERTIFICATES_DIR / f"qr_{cert_id}.png"
        qr = qrcode.make(f"https://t.me/your_bot?start=cert_{cert_id}")
        qr.save(str(qr_path))
        self.image(str(qr_path), x=245, y=145, w=35)

def generate_certificate(name: str, course: str) -> bytes:
    date_str = datetime.now().strftime("%B %d, %Y")
    cert_id = hashlib.sha256(f"{name}{course}{date_str}{datetime.now()}".encode()).hexdigest()[:12].upper()
    pdf = CertificatePDF()
    pdf.create_certificate(name, course, date_str, cert_id)
    output = pdf.output(dest="S")
    # fpdf2 v2.8+ returns bytearray, not str
    pdf_bytes = bytes(output) if isinstance(output, bytearray) else output.encode("latin-1")
    return pdf_bytes, cert_id

# ============== BOT HANDLERS ==============
MENU, SCHEDULE, LESSON, QUIZ, SETTINGS, QUIZ_FLOW = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = register_student(user.id, user.first_name, user.username)

    welcome_msg = (
        f"👋 Salaan, {user.first_name}!\n\n"
        f"📚 *MACALLIN AI KOORSO BOT*\n"
        f"Waxaan kuu soo gudbinayaa casharada week kasta si habboon.\n\n"
    )

    if is_new:
        welcome_msg += (
            "✅ Waad ku diiwaan gashan tahay!\n"
            "🗓 Koorsooyinku waxay qaadanayaan *14 usbuuc* (70 cashar).\n"
            "📅 Usbuuc kasta: *5 cashar*\n"
            "🎯 Quiz ka dib cashar kasta!\n"
            "📜 Certificate marka la dhammaystiro!\n\n"
            "Dooro waxa aad rabto hoos:"
        )
    else:
        welcome_msg += "Ku soo dhawow mar kale! Dooro waxa aad rabto:"

    keyboard = [
        [InlineKeyboardButton("📅 Arag Schedule-ka", callback_data="schedule")],
        [InlineKeyboardButton("📖 Casharada Usbuucan", callback_data="current_week")],
        [InlineKeyboardButton("🎯 Quiz Ciyaar", callback_data="quiz_menu")],
        [InlineKeyboardButton("📊 Xogtaada", callback_data="my_progress")],
        [InlineKeyboardButton("📜 Certificate-ka", callback_data="certificate")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("🆘 Caawimaad", callback_data="help")],
    ]

    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("📅 Arag Schedule-ka", callback_data="schedule")],
        [InlineKeyboardButton("📖 Casharada Usbuucan", callback_data="current_week")],
        [InlineKeyboardButton("🎯 Quiz Ciyaar", callback_data="quiz_menu")],
        [InlineKeyboardButton("📊 Xogtaada", callback_data="my_progress")],
        [InlineKeyboardButton("📜 Certificate-ka", callback_data="certificate")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("🆘 Caawimaad", callback_data="help")],
    ]

    text = "👨‍🏫 *MACALLIN BOT v2.0 — Menu Guud*\n\nDooro waxa aad rabto:"

    if query:
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

# ============== SCHEDULE ==============
async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    schedule = generate_schedule()
    text = "📅 *SCHEDULE-GUUD (14 Usbuuc)*\n\n"

    for week in schedule[:8]:
        text += f"*Usbuuca {week['week']}* ({week['start_date']} - {week['end_date']})\n"
        for lesson in week["lessons"]:
            short_course = lesson["course_name"].replace("KOORSADA ", "K")
            text += f"  • {short_course}: {lesson['title']}\n"
        text += "\n"

    text += "... iyo waxyaabo kale\n"

    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# ============== CURRENT WEEK ==============
async def show_current_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)

    if not student:
        await query.edit_message_text("Fadlan /start marka hore.")
        return

    current_week = student.get("current_week", 1)
    schedule = generate_schedule()

    week_data = None
    for w in schedule:
        if w["week"] == current_week:
            week_data = w
            break

    if not week_data:
        await query.edit_message_text("🎉 Hamdulillah! Waxaad dhammaystirtay koorsada!")
        return

    text = f"📖 *CASHARADA USBUUCA {current_week}*\n"
    text += f"_{week_data['start_date']} - {week_data['end_date']}_\n\n"

    buttons = []
    for lesson in week_data["lessons"]:
        status = "✅" if lesson["title"] in student.get("completed_lessons", []) else "⬜"
        quiz_done = "🎯" if lesson["title"] in student.get("quiz_scores", {}) else ""
        text += f"{status}{quiz_done} *{lesson['course_name']}*\n"
        text += f"   Cashar {lesson['lesson_number']}: {lesson['title']}\n"
        text += f"   🔗 [Riix halkan]({lesson['link']})\n\n"

        row = [InlineKeyboardButton(
            f"✅ Dhammaystir: {lesson['title'][:20]}...",
            callback_data=f"complete_{lesson['title']}"
        )]
        # Haddii quiz jiro, ku dar button
        if get_quiz_for_lesson(lesson["title"]):
            row.append(InlineKeyboardButton(
                "🎯 Quiz",
                callback_data=f"quiz_start_{lesson['title']}"
            ))
        buttons.append(row)

    buttons.append([InlineKeyboardButton("▶️ Usbuuca Xiga ➡️", callback_data="next_week")])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

# ============== COMPLETE LESSON ==============
async def complete_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lesson_title = query.data.replace("complete_", "")

    update_progress(user_id, completed_lesson=lesson_title)

    # Check certificate eligibility
    student = db.get_student(user_id)
    total = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))
    if completed >= total and not student.get("certificate_issued"):
        await query.answer("🎓 Koorsada waa la dhammaystiray! Riix /certificate!", show_alert=True)
    else:
        await query.answer(f"✅ {lesson_title[:30]}... waa la dhammaystiray!", show_alert=True)

    await show_current_week(update, context)

# ============== NEXT WEEK ==============
async def next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)
    current = student.get("current_week", 1)
    update_progress(user_id, week=current + 1)

    await query.answer("🎉 Usbuuca xiga waa la furay!")
    await show_current_week(update, context)

# ============== PROGRESS ==============
async def my_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)

    if not student:
        await query.edit_message_text("Fadlan /start marka hore.")
        return

    total_lessons = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))
    percent = int((completed / total_lessons) * 100)
    current_week = student.get("current_week", 1)
    quiz_count = len(student.get("quiz_scores", {}))

    text = (
        f"📊 *XOGTAADA*\n\n"
        f"👤 Magac: {student['first_name']}\n"
        f"📅 Biirta: {student['joined']}\n"
        f"📖 Usbuuca Hadda: {current_week}\n"
        f"✅ Cashar la dhammaystiray: {completed}/{total_lessons}\n"
        f"🎯 Quiz la qabtay: {quiz_count}\n"
        f"📈 Qaybta la dhammaystiray: {percent}%\n\n"
    )

    bar_len = 20
    filled = int(bar_len * percent / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    text += f"[{bar}] {percent}%\n\n"

    if percent >= 100:
        text += "🎓 *Hambalyo! Waxaad dhammaystirtay koorsada!*\n"
        text += "Riix 📜 Certificate si aad u hesho caddayntaada."
    else:
        text += "Sii wad dadaalka! 💪"

    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# ============== QUIZ SYSTEM ==============
async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if not student:
        await query.edit_message_text("Fadlan /start marka hore.")
        return

    # List all available quizzes for completed + current lessons
    text = "🎯 *QUIZ MENU*\n\nDooro cashar aad quiz u rabto:\n\n"
    buttons = []

    all_lessons = []
    for course in COURSES:
        for lesson in course["lessons"]:
            all_lessons.append(lesson["title"])

    for lesson_title in all_lessons:
        quiz = get_quiz_for_lesson(lesson_title)
        if quiz:
            done = "✅" if lesson_title in student.get("quiz_scores", {}) else "⬜"
            buttons.append([InlineKeyboardButton(
                f"{done} {lesson_title[:35]}",
                callback_data=f"quiz_start_{lesson_title}"
            )])

    if not buttons:
        text = "🎯 *QUIZ*\n\nHadda ma jiraan quiz-yo la diyaariyay. Waxaan kuu soo gudbinayaa marka xiga!"

    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
    )

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lesson_title = query.data.replace("quiz_start_", "")
    quiz = get_quiz_for_lesson(lesson_title)

    if not quiz:
        await query.answer("Quiz lama diyaarin casharkan!", show_alert=True)
        return

    # Initialize quiz session in context.user_data
    context.user_data["quiz"] = {
        "lesson": lesson_title,
        "questions": quiz,
        "current": 0,
        "correct": 0,
    }

    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data.get("quiz")
    if not quiz:
        return

    q_idx = quiz["current"]
    if q_idx >= len(quiz["questions"]):
        # Quiz done
        total = len(quiz["questions"])
        correct = quiz["correct"]
        percent = int((correct / total) * 100)
        lesson = quiz["lesson"]

        user_id = update.effective_user.id
        update_progress(user_id, quiz_score={"lesson": lesson, "score": percent})

        text = (
            f"🎯 *QUIZ DHAMMAYSTIRAN!*\n\n"
            f"Cashar: {lesson}\n"
            f"Jawaabto sax ah: {correct}/{total}\n"
            f"Qaybta saxda ah: {percent}%\n\n"
        )

        if percent == 100:
            text += "🏆 *PERFECT! Aad baad u wanaagsan tahay!*"
        elif percent >= 80:
            text += "⭐ *Waa wanaagsan tahay!*"
        elif percent >= 50:
            text += "👍 *Waa fiican tahay, sii wad!*"
        else:
            text += "📚 *Fadlan dib u eeg casharka si aad u barato.*"

        keyboard = [
            [InlineKeyboardButton("🎯 Quiz Kale", callback_data="quiz_menu")],
            [InlineKeyboardButton("📖 Casharada", callback_data="current_week")],
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
        ]

        if hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
        return

    q = quiz["questions"][q_idx]
    text = f"🎯 *QUIZ — Cashar: {quiz['lesson']}*\n\n"
    text += f"*Su'aal {q_idx + 1}/{len(quiz['questions'])}*\n"
    text += f"{q['q']}\n\n"

    buttons = []
    for idx, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(
            f"{chr(65+idx)}. {opt}",
            callback_data=f"quiz_ans_{idx}"
        )])

    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
        )

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quiz = context.user_data.get("quiz")
    if not quiz:
        return

    ans_idx = int(query.data.replace("quiz_ans_", ""))
    q_idx = quiz["current"]
    correct_idx = quiz["questions"][q_idx]["correct"]

    if ans_idx == correct_idx:
        quiz["correct"] += 1
        await query.answer("✅ SAX!")
    else:
        correct_opt = quiz["questions"][q_idx]["options"][correct_idx]
        await query.answer(f"❌ Khalad! Jawaabta saxda ah: {correct_opt}", show_alert=True)

    quiz["current"] += 1
    await ask_question(update, context)

# ============== CERTIFICATE ==============
async def certificate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    student = db.get_student(user_id)

    if not student:
        if query:
            await query.answer()
            await query.edit_message_text("Fadlan /start marka hore.")
        else:
            await update.message.reply_text("Fadlan /start marka hore.")
        return

    total_lessons = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))

    if completed < total_lessons:
        text = (
            f"📜 *CERTIFICATE*\n\n"
            f"Wali ma ahan inaad hesho caddaynta.\n"
            f"Waxaad u baahan tahay inaad dhammaystirto dhammaan 70 cashar.\n\n"
            f"Hadda: {completed}/{total_lessons} cashar la dhammaystiray.\n"
            f"Sii wad! 💪"
        )
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        if query:
            await query.answer()
            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
        return

    # Generate certificate
    if query:
        await query.answer("⏳ Caddaynta la sameynayaa...")
    else:
        await update.message.reply_text("⏳ Caddaynta la sameynayaa...")

    name = student.get("first_name", "Student")
    course = "MACALLIN AI — 70 Cashar Course"
    pdf_bytes, cert_id = generate_certificate(name, course)

    # Mark certificate as issued
    student["certificate_issued"] = True
    student["certificate_id"] = cert_id
    db.save_student(str(user_id), student)

    # Send PDF
    pdf_file = InputFile(io.BytesIO(pdf_bytes), filename=f"Certificate_{name}_{cert_id}.pdf")

    if query:
        await query.edit_message_text("📜 Caddaynta waa la diyaariyay! Waxaan kuu soo dirayaa hadda...")
        await context.bot.send_document(
            chat_id=user_id,
            document=pdf_file,
            caption=(
                f"🎓 *HAMBALYO {name}!*\n\n"
                f"Waxaad si guul ah u dhammaystirtay *MACALLIN AI Course*!\n"
                f"📜 Certificate ID: `{cert_id}`\n"
                f"🔍 Hubi caddayntaada QR code-ka ku yaal."
            ),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_document(
            document=pdf_file,
            caption=(
                f"🎓 *HAMBALYO {name}!*\n\n"
                f"Waxaad si guul ah u dhammaystirtay *MACALLIN AI Course*!\n"
                f"📜 Certificate ID: `{cert_id}`\n"
                f"🔍 Hubi caddayntaada QR code-ka ku yaal."
            ),
            parse_mode="Markdown",
        )

# ============== SETTINGS ==============
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)
    reminders = student.get("reminders", True)

    status = "🔔 ON" if reminders else "🔕 OFF"
    keyboard = [
        [InlineKeyboardButton(f"Xusuusin Usbuucii {status}", callback_data="toggle_reminders")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
    ]

    await query.edit_message_text(
        f"⚙️ *Settings*\n\nXusuusinada usbuucii: {status}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

async def toggle_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if student:
        student["reminders"] = not student.get("reminders", True)
        db.save_student(str(user_id), student)
    await settings(update, context)

# ============== HELP ==============
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    text = (
        "🆘 *CAAWIMAAD*\n\n"
        "📌 */start* — Bot ku soo noqo\n"
        "📌 */schedule* — Arag dhammaan schedule-ka\n"
        "📌 */week* — Casharada usbuuca hadda\n"
        "📌 */progress* — Arag horumarkaaga\n"
        "📌 */quiz* — Ciyaar Quiz\n"
        "📌 */certificate* — Hesho caddayntaada PDF\n"
        "📌 */next* — U gudub usbuuca xiga\n"
        "📌 */help* — Caawimaad\n\n"
        "Haddii aad welwel qabto, la xiriir @YourUsername"
    )

    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    if query:
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

# ============== DIRECT COMMANDS ==============
class FakeQuery:
    def __init__(self, msg):
        self._msg = msg
    async def answer(self):
        pass
    async def edit_message_text(self, *a, **kw):
        await self._msg.reply_text(*a, **kw)

async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.callback_query = FakeQuery(update.message)
    await show_schedule(update, context)

async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.callback_query = FakeQuery(update.message)
    await show_current_week(update, context)

async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.callback_query = FakeQuery(update.message)
    await my_progress(update, context)

async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.callback_query = FakeQuery(update.message)
    await quiz_menu(update, context)

async def cmd_certificate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await certificate_cmd(update, context)

async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if student:
        current = student.get("current_week", 1)
        update_progress(user_id, week=current + 1)
        await update.message.reply_text(f"✅ Usbuuca {current + 1} waa la furay! Riix /week si aad u aragto casharada.")
    else:
        await update.message.reply_text("Fadlan /start marka hore.")

# ============== ADMIN ==============
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Loo ogolaanshahani ma aha.")
        return

    if not context.args:
        await update.message.reply_text("Fadlan qor fariin: /broadcast Fariinta halkan")
        return

    message = " ".join(context.args)
    students = db.all_students()
    sent = 0
    failed = 0

    for uid, student in students.items():
        try:
            await context.bot.send_message(
                chat_id=student["user_id"],
                text=f"📢 *FARIIN CUSUB*\n\n{message}",
                parse_mode="Markdown",
            )
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send to {uid}: {e}")
            failed += 1

    await update.message.reply_text(f"✅ {sent} oo arday ah waa la diray. ❌ {failed} ma ahan.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Loo ogolaanshahani ma aha.")
        return

    students = db.all_students()
    total = len(students)
    active = sum(1 for s in students.values() if s.get("active", True))
    cert_issued = sum(1 for s in students.values() if s.get("certificate_issued", False))

    text = (
        f"📊 *TIRAKOOBKA ARDAYDA*\n\n"
        f"👥 Wadarta ardayda: {total}\n"
        f"✅ Kuwa firfircoon: {active}\n"
        f"📜 Certificates la bixiyay: {cert_issued}\n\n"
    )

    progress_list = []
    for uid, s in students.items():
        completed = len(s.get("completed_lessons", []))
        quiz_count = len(s.get("quiz_scores", {}))
        progress_list.append((s["first_name"], completed, quiz_count, s.get("current_week", 1)))

    progress_list.sort(key=lambda x: x[1], reverse=True)
    text += "🏆 *Ardayda ugu horreeya:*\n"
    for name, comp, quiz, week in progress_list[:5]:
        text += f"  • {name}: {comp} cashar | {quiz} quiz (W{week})\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ============== AUTO-REMINDERS ==============
async def weekly_reminder(context: ContextTypes.DEFAULT_TYPE):
    students = db.all_students()
    schedule = generate_schedule()

    for uid, student in students.items():
        if not student.get("reminders", True):
            continue

        current_week = student.get("current_week", 1)
        week_data = None
        for w in schedule:
            if w["week"] == current_week:
                week_data = w
                break

        if not week_data:
            continue

        text = (
            f"📅 *XUSUUSIN USBUUCA {current_week}*\n\n"
            f"Salaan {student['first_name']}!\n"
            f"Casharada usbuucan ee cusub:\n\n"
        )

        for lesson in week_data["lessons"]:
            text += f"• {lesson['title']}\n"

        text += "\nRiix /week si aad u aragto dhammaan faahfaahinta."
        text += "\n🎯 Quiz-ga ka ciyaar si aad u hagaajiso!"

        try:
            await context.bot.send_message(
                chat_id=student["user_id"],
                text=text,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Reminder failed for {uid}: {e}")

# ============== MAIN ==============
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Callbacks
    application.add_handler(CallbackQueryHandler(show_schedule, pattern="^schedule$"))
    application.add_handler(CallbackQueryHandler(show_current_week, pattern="^current_week$"))
    application.add_handler(CallbackQueryHandler(my_progress, pattern="^my_progress$"))
    application.add_handler(CallbackQueryHandler(complete_lesson, pattern="^complete_"))
    application.add_handler(CallbackQueryHandler(next_week, pattern="^next_week$"))
    application.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(settings, pattern="^settings$"))
    application.add_handler(CallbackQueryHandler(toggle_reminders, pattern="^toggle_reminders$"))
    application.add_handler(CallbackQueryHandler(help_cmd, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(quiz_menu, pattern="^quiz_menu$"))
    application.add_handler(CallbackQueryHandler(quiz_start, pattern="^quiz_start_"))
    application.add_handler(CallbackQueryHandler(quiz_answer, pattern="^quiz_ans_"))
    application.add_handler(CallbackQueryHandler(certificate_cmd, pattern="^certificate$"))

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", cmd_schedule))
    application.add_handler(CommandHandler("week", cmd_week))
    application.add_handler(CommandHandler("progress", cmd_progress))
    application.add_handler(CommandHandler("quiz", cmd_quiz))
    application.add_handler(CommandHandler("certificate", cmd_certificate))
    application.add_handler(CommandHandler("next", cmd_next))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("stats", admin_stats))

    # Reminder (Isniinta 09:00)
    job_queue = application.job_queue
    job_queue.run_repeating(
        weekly_reminder,
        interval=timedelta(days=7),
        first=datetime.strptime("2026-07-21 09:00:00", "%Y-%m-%d %H:%M:%S")
    )

    print("🤖 MACALLIN BOT v2.0 waa la shidlay!")
    print("   ✅ Quiz Automatic")
    print("   ✅ Certificate PDF")
    print("   ✅ Firebase Database (Optional)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
