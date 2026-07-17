"""
MACALLIN BOT - Core Application
Waa qaybta dhexe ee bot-ka (webhook & polling wadaag)
"""
import os
import json
import io
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== CONFIG ==============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

DATA_FILE = Path(__file__).parent.parent / "students.json"
CERTIFICATES_DIR = Path(__file__).parent.parent / "certificates"
CERTIFICATES_DIR.mkdir(exist_ok=True)

# Import course data
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from course_data import COURSES, LESSONS_PER_WEEK, generate_schedule

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

def get_quiz_for_lesson(lesson_title: str):
    for course_quizzes in QUIZ_DATA.values():
        if lesson_title in course_quizzes:
            return course_quizzes[lesson_title]
    return None

# ============== DATABASE ==============
class Database:
    def load_students(self) -> Dict[str, Any]:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_student(self, user_id: str, data: dict):
        students = self.load_students()
        students[user_id] = data
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=2)

    def get_student(self, user_id: str) -> Optional[dict]:
        return self.load_students().get(str(user_id))

    def all_students(self) -> Dict[str, Any]:
        return self.load_students()

db = Database()

# ============== STUDENT FUNCTIONS ==============
def register_student(user_id, first_name, username=""):
    uid = str(user_id)
    if db.get_student(user_id):
        return False
    data = {
        "user_id": user_id,
        "first_name": first_name,
        "username": username,
        "joined": str(datetime.now().date()),
        "current_week": 1,
        "completed_lessons": [],
        "quiz_scores": {},
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

# ============== PDF CERTIFICATE ==============
class CertificatePDF:
    def header(self):
        pass
    def __init__(self):
        self.pdf = None

from fpdf import FPDF
import qrcode

class CertPDF(FPDF):
    def header(self):
        self.set_fill_color(26, 26, 46)
        self.rect(0, 0, 297, 210, "F")

def generate_certificate(name: str, course: str):
    date_str = datetime.now().strftime("%B %d, %Y")
    cert_id = hashlib.sha256(f"{name}{course}{date_str}{datetime.now()}".encode()).hexdigest()[:12].upper()

    pdf = CertPDF()
    pdf.add_page("L", "A4")
    pdf.set_auto_page_break(False)

    pdf.set_draw_color(255, 215, 0)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1)
    pdf.rect(15, 15, 267, 180)

    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(255, 215, 0)
    pdf.set_y(35)
    pdf.cell(0, 20, "MACALLIN AI", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 12, "CERTIFICATE OF COMPLETION", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_draw_color(255, 215, 0)
    pdf.line(80, 75, 217, 75)

    pdf.set_y(90)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 10, "This certificate is proudly presented to", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(105)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, name, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(130)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 10, "For successfully completing the course:", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 212, 255)
    pdf.cell(0, 12, course, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(160)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, f"Date: {date_str}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"ID: {cert_id}", align="C", new_x="LMARGIN", new_y="NEXT")

    qr_path = CERTIFICATES_DIR / f"qr_{cert_id}.png"
    qr = qrcode.make(f"https://t.me/check_cert_{cert_id}")
    qr.save(str(qr_path))
    pdf.image(str(qr_path), x=245, y=145, w=35)

    output = pdf.output(dest="S")
    pdf_bytes = bytes(output) if isinstance(output, bytearray) else output.encode("latin-1")
    return pdf_bytes, cert_id

# ============== KEYBOARD ==============
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Schedule", callback_data="schedule")],
        [InlineKeyboardButton("📖 Casharada Usbuucan", callback_data="current_week")],
        [InlineKeyboardButton("🎯 Quiz Ciyaar", callback_data="quiz_menu")],
        [InlineKeyboardButton("📊 Xogtaada", callback_data="my_progress")],
        [InlineKeyboardButton("📜 Certificate", callback_data="certificate")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("🆘 Caawimaad", callback_data="help")],
    ])

# ============== HANDLERS ==============
MENU = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = register_student(user.id, user.first_name, user.username or "")

    welcome = (
        f"👋 Salaan, {user.first_name}!\n\n"
        f"📚 *MACALLIN AI KOORSO BOT*\n"
        f"70 cashar | 14 usbuuc | Quiz + Certificate\n\n"
    )
    if is_new:
        welcome += "✅ Waad ku diiwaan gashan tahay! Dooro hoose:"
    else:
        welcome += "Ku soo dhawow mar kale!"

    await update.message.reply_text(welcome, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    return MENU

async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    schedule = generate_schedule()
    text = "📅 *SCHEDULE (14 Usbuuc)*\n\n"
    for week in schedule[:6]:
        text += f"*W{week['week']}* ({week['start_date']})\n"
        for lesson in week["lessons"][:2]:
            text += f"  • {lesson['title'][:30]}\n"
        text += "\n"
    text += "... iyo waxyaabo kale\n"
    await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def show_current_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if not student:
        await query.edit_message_text("Fadlan /start")
        return

    current_week = student.get("current_week", 1)
    schedule = generate_schedule()
    week_data = next((w for w in schedule if w["week"] == current_week), None)

    if not week_data:
        await query.edit_message_text("🎉 Koorsada waa la dhammaystiray!")
        return

    text = f"📖 *USBUUCA {current_week}*\n_{week_data['start_date']}_{week_data['end_date']}_\n\n"
    buttons = []
    for lesson in week_data["lessons"]:
        done = "✅" if lesson["title"] in student.get("completed_lessons", []) else "⬜"
        text += f"{done} {lesson['title']}\n"
        row = [InlineKeyboardButton(f"✅ {lesson['title'][:20]}...", callback_data=f"complete_{lesson['title']}")]
        if get_quiz_for_lesson(lesson["title"]):
            row.append(InlineKeyboardButton("🎯 Quiz", callback_data=f"quiz_{lesson['title']}"))
        buttons.append(row)

    buttons.append([InlineKeyboardButton("➡️ Usbuuca Xiga", callback_data="next_week")])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown", disable_web_page_preview=True)

async def complete_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lesson_title = query.data.replace("complete_", "")
    update_progress(user_id, completed_lesson=lesson_title)
    await query.answer("✅ Waa la dhammaystiray!", show_alert=True)
    await show_current_week(update, context)

async def next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    student = db.get_student(user_id)
    current = student.get("current_week", 1)
    update_progress(user_id, week=current + 1)
    await show_current_week(update, context)

async def my_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if not student:
        await query.edit_message_text("Fadlan /start")
        return

    total = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))
    percent = int((completed / total) * 100)
    bar = "█" * int(20 * percent / 100) + "░" * (20 - int(20 * percent / 100))

    text = (
        f"📊 *XOGTAADA*\n\n"
        f"👤 {student['first_name']}\n"
        f"📖 Usbuuc: {student.get('current_week', 1)}\n"
        f"✅ Cashar: {completed}/{total}\n"
        f"🎯 Quiz: {len(student.get('quiz_scores', {}))}\n"
        f"📈 [{bar}] {percent}%\n"
    )
    await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚙️ *Settings*\n\nXusuusin: ON\n\nHorey ayaa loo sameeyay.", reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    text = (
        "🆘 *CAAWIMAAD*\n\n"
        "/start — Bot ku soo noqo\n"
        "/week — Casharada\n"
        "/progress — Horumarka\n"
        "/quiz — Quiz ciyaar\n"
        "/certificate — Caddayn\n"
        "/help — Caawimaad"
    )
    if query:
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    text = "👨‍🏫 *MACALLIN BOT*\n\nDooro waxa aad rabto:"
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def certificate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    student = db.get_student(user_id)
    if not student:
        text = "Fadlan /start"
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    total = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))

    if completed < total:
        text = f"📜 Wali ma ahan! {completed}/{total} cashar. Sii wad! 💪"
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        return

    # Dhammaystiran — samee PDF
    if update.callback_query:
        await update.callback_query.answer("⏳ Caddaynta la sameynayaa...")
    else:
        await update.message.reply_text("⏳ Caddaynta la sameynayaa...")

    pdf_bytes, cert_id = generate_certificate(student["first_name"], "MACALLIN AI — 70 Cashar")

    student["certificate_issued"] = True
    student["certificate_id"] = cert_id
    db.save_student(str(user_id), student)

    pdf_file = InputFile(io.BytesIO(pdf_bytes), filename=f"Certificate_{student['first_name']}_{cert_id}.pdf")
    caption = f"🎓 *HAMBALYO {student['first_name']}!*\n📜 ID: `{cert_id}`"

    if update.callback_query:
        await context.bot.send_document(
            chat_id=user_id,
            document=pdf_file,
            caption=caption,
            parse_mode="Markdown",
        )
        await update.callback_query.edit_message_text("📜 Caddaynta waa la soo diray! 🎓", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_document(
            document=pdf_file,
            caption=caption,
            parse_mode="Markdown",
        )

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🎯 *QUIZ MENU*\n\nDooro cashar:"
    buttons = []
    for course in COURSES:
        for lesson in course["lessons"]:
            if get_quiz_for_lesson(lesson["title"]):
                buttons.append([InlineKeyboardButton(lesson["title"][:40], callback_data=f"quiz_{lesson['title']}")])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lesson_title = query.data.replace("quiz_", "")
    quiz = get_quiz_for_lesson(lesson_title)
    if not quiz:
        await query.answer("Quiz lama diyaarin!", show_alert=True)
        return

    context.user_data["quiz"] = {"lesson": lesson_title, "questions": quiz, "current": 0, "correct": 0}
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data.get("quiz")
    if not quiz:
        return
    q_idx = quiz["current"]
    if q_idx >= len(quiz["questions"]):
        total = len(quiz["questions"])
        correct = quiz["correct"]
        percent = int((correct / total) * 100)
        lesson = quiz["lesson"]
        user_id = update.effective_user.id
        update_progress(user_id, quiz_score={"lesson": lesson, "score": percent})

        text = f"🎯 *QUIZ DHAMMAYSTIRAN!*\n\nCashar: {lesson}\nJawaab sax: {correct}/{total} ({percent}%)\n\n"
        if percent == 100:
            text += "🏆 PERFECT!"
        elif percent >= 80:
            text += "⭐ Waa wanaagsan tahay!"
        elif percent >= 50:
            text += "👍 Waa fiican tahay!"
        else:
            text += "📚 Dib u eeg casharka."

        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        if hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    q = quiz["questions"][q_idx]
    text = f"🎯 *QUIZ* ({quiz['lesson']})\n\nSu'aal {q_idx + 1}/{len(quiz['questions'])}:\n{q['q']}\n\n"
    buttons = []
    for idx, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(f"{chr(65+idx)}. {opt}", callback_data=f"quizans_{idx}")])
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quiz = context.user_data.get("quiz")
    if not quiz:
        return
    ans_idx = int(query.data.replace("quizans_", ""))
    q_idx = quiz["current"]
    correct_idx = quiz["questions"][q_idx]["correct"]
    if ans_idx == correct_idx:
        quiz["correct"] += 1
        await query.answer("✅ SAX!")
    else:
        correct_opt = quiz["questions"][q_idx]["options"][correct_idx]
        await query.answer(f"❌ Jawaabta saxda ah: {correct_opt}", show_alert=True)
    quiz["current"] += 1
    await ask_question(update, context)

# ============== BUILD APPLICATION ==============
def build_application():
    """Samee Application-ka oo ku dar handlers"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Callbacks
    application.add_handler(CallbackQueryHandler(show_schedule, pattern="^schedule$"))
    application.add_handler(CallbackQueryHandler(show_current_week, pattern="^current_week$"))
    application.add_handler(CallbackQueryHandler(my_progress, pattern="^my_progress$"))
    application.add_handler(CallbackQueryHandler(complete_lesson, pattern="^complete_"))
    application.add_handler(CallbackQueryHandler(next_week, pattern="^next_week$"))
    application.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(settings, pattern="^settings$"))
    application.add_handler(CallbackQueryHandler(help_cmd, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(quiz_menu, pattern="^quiz_menu$"))
    application.add_handler(CallbackQueryHandler(quiz_start, pattern="^quiz_"))
    application.add_handler(CallbackQueryHandler(quiz_answer, pattern="^quizans_"))
    application.add_handler(CallbackQueryHandler(certificate_cmd, pattern="^certificate$"))

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("certificate", certificate_cmd))

    return application
