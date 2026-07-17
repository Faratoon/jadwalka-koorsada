"""
MACALLIN TELEGRAM BOT - Automation Course Bot
Waxaa sameeya: Weekly schedule, progress tracking, auto-lesson delivery
Habka isticmaalka:
    1. BotFather ka samee bot cusub, qaado TOKEN-ka
    2. python-telegram-bot ku shub: pip install python-telegram-bot
    3. BOT_TOKEN ku beddel meelaha ku qoran TOKEN-KAAGA
    4. Bot shaqeli: python telegram_course_bot.py
"""

import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ============== DEJIMAHA MUHIIMKA AH ==============
# TOKEN-kaaga halkan geli:
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]  # Telegram ID-gaaga (ku hel @userinfobot)

DATA_FILE = Path(__file__).parent / "students.json"
SCHEDULE_FILE = Path(__file__).parent / "schedule.json"

# Casharada (waxaan ka soo xiganay course_data.py)
from course_data import COURSES, LESSONS_PER_WEEK, generate_schedule

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== XOGTA ARDAYDA ==============
def load_students():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_students(students):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)

def get_student(user_id):
    students = load_students()
    return students.get(str(user_id), None)

def register_student(user_id, first_name, username=""):
    students = load_students()
    if str(user_id) not in students:
        students[str(user_id)] = {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "joined": str(datetime.now().date()),
            "current_week": 1,
            "completed_lessons": [],
            "active": True,
            "reminders": True,
        }
        save_students(students)
        return True
    return False

def update_progress(user_id, week=None, completed_lesson=None):
    students = load_students()
    uid = str(user_id)
    if uid in students:
        if week is not None:
            students[uid]["current_week"] = week
        if completed_lesson is not None:
            if completed_lesson not in students[uid]["completed_lessons"]:
                students[uid]["completed_lessons"].append(completed_lesson)
        save_students(students)

# ============== WADA HADALKA (CONVERSATION) ==============
MENU, SCHEDULE, LESSON, QUIZ, SETTINGS = range(5)

# ============== AMARKA /start ==============
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
            "📅 Usbuuc kasta: *5 cashar*\n\n"
            "Dooro waxa aad rabto hoos:"
        )
    else:
        welcome_msg += "Ku soo dhawow mar kale! Dooro waxa aad rabto:"

    keyboard = [
        [InlineKeyboardButton("📅 Arag Schedule-ka", callback_data="schedule")],
        [InlineKeyboardButton("📖 Casharada Usbuucan", callback_data="current_week")],
        [InlineKeyboardButton("📊 Xogtaada", callback_data="my_progress")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("🆘 Caawimaad", callback_data="help")],
    ]

    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )
    return MENU

# ============== SCHEDULE ==============
async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    schedule = generate_schedule()
    text = "📅 *SCHEDULE-GUUD (14 Usbuuc)*\n\n"

    for week in schedule[:8]:  # Muuji 8 usbuuc ee ugu horreeya
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

# ============== CASHARADA USBUUCA ==============
async def show_current_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = get_student(user_id)

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
        status = "✅" if lesson["title"] in student["completed_lessons"] else "⬜"
        text += f"{status} *{lesson['course_name']}*\n"
        text += f"   Cashar {lesson['lesson_number']}: {lesson['title']}\n"
        text += f"   🔗 [Riix halkan]({lesson['link']})\n\n"

        buttons.append(
            [InlineKeyboardButton(
                f"✅ Dhammaystir: {lesson['title'][:25]}...",
                callback_data=f"complete_{lesson['title']}"
            )]
        )

    buttons.append([InlineKeyboardButton("▶️ Usbuuca Xiga ➡️", callback_data="next_week")])
    buttons.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

# ============== DHAMMAYSTIR CASHAR ==============
async def complete_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lesson_title = query.data.replace("complete_", "")

    update_progress(user_id, completed_lesson=lesson_title)

    await query.answer(f"✅ {lesson_title} waa la dhammaystiray!", show_alert=True)
    await show_current_week(update, context)

# ============== USBUUCA XIGA ==============
async def next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = get_student(user_id)
    current = student.get("current_week", 1)
    update_progress(user_id, week=current + 1)

    await query.answer("🎉 Usbuuca xiga waa la furay!")
    await show_current_week(update, context)

# ============== XOGTA ARDAYGA ==============
async def my_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = get_student(user_id)

    if not student:
        await query.edit_message_text("Fadlan /start marka hore.")
        return

    total_lessons = sum(len(c["lessons"]) for c in COURSES)
    completed = len(student.get("completed_lessons", []))
    percent = int((completed / total_lessons) * 100)
    current_week = student.get("current_week", 1)

    text = (
        f"📊 *XOGTAADA*\n\n"
        f"👤 Magac: {student['first_name']}\n"
        f"📅 Biirta: {student['joined']}\n"
        f"📖 Usbuuca Hadda: {current_week}\n"
        f"✅ Cashar la dhammaystiray: {completed}/{total_lessons}\n"
        f"📈 Qaybta la dhammaystiray: {percent}%\n\n"
    )

    # Progress bar
    bar_len = 20
    filled = int(bar_len * percent / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    text += f"[{bar}] {percent}%\n\n"

    text += "Sii wad dadaalka! 💪"

    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# ============== MENU ==============
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("📅 Arag Schedule-ka", callback_data="schedule")],
        [InlineKeyboardButton("📖 Casharada Usbuucan", callback_data="current_week")],
        [InlineKeyboardButton("📊 Xogtaada", callback_data="my_progress")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("🆘 Caawimaad", callback_data="help")],
    ]

    text = "👨‍🏫 *MACALLIN BOT - Menu Guud*\n\nDooro waxa aad rabto:"

    if query:
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

# ============== SETTINGS ==============
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    student = get_student(user_id)
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
    students = load_students()
    uid = str(user_id)
    if uid in students:
        students[uid]["reminders"] = not students[uid].get("reminders", True)
        save_students(students)

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

# ============== AMARKA DIREECT ==============
async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create a fake callback_query object for reuse
    class FakeQuery:
        def __init__(self, msg):
            self._msg = msg
        async def answer(self):
            pass
        async def edit_message_text(self, *a, **kw):
            await self._msg.reply_text(*a, **kw)

    update.callback_query = FakeQuery(update.message)
    await show_schedule(update, context)

async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    class FakeQuery:
        def __init__(self, msg):
            self._msg = msg
        async def answer(self):
            pass
        async def edit_message_text(self, *a, **kw):
            await self._msg.reply_text(*a, **kw)

    update.callback_query = FakeQuery(update.message)
    await show_current_week(update, context)

async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    class FakeQuery:
        def __init__(self, msg):
            self._msg = msg
        async def answer(self):
            pass
        async def edit_message_text(self, *a, **kw):
            await self._msg.reply_text(*a, **kw)

    update.callback_query = FakeQuery(update.message)
    await my_progress(update, context)

async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    student = get_student(user_id)
    if student:
        current = student.get("current_week", 1)
        update_progress(user_id, week=current + 1)
        await update.message.reply_text(f"✅ Usbuuca {current + 1} waa la furay! Riix /week si aad u aragto casharada.")
    else:
        await update.message.reply_text("Fadlan /start marka hore.")

# ============== AMARKA ADMIN ==============
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Loo ogolaanshahani ma aha.")
        return

    if not context.args:
        await update.message.reply_text("Fadlan qor fariin: /broadcast Fariinta halkan")
        return

    message = " ".join(context.args)
    students = load_students()
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

    students = load_students()
    total = len(students)
    active = sum(1 for s in students.values() if s.get("active", True))

    text = (
        f"📊 *TIRAKOOBKA ARDAYDA*\n\n"
        f"👥 Wadarta ardayda: {total}\n"
        f"✅ Kuwa firfircoon: {active}\n\n"
    )

    # Top 5 students by progress
    progress_list = []
    for uid, s in students.items():
        completed = len(s.get("completed_lessons", []))
        progress_list.append((s["first_name"], completed, s.get("current_week", 1)))

    progress_list.sort(key=lambda x: x[1], reverse=True)
    text += "🏆 *Ardayda ugu horreeya:*\n"
    for name, comp, week in progress_list[:5]:
        text += f"  • {name}: {comp} cashar (Usbuuc {week})\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ============== AUTO-REMINDERS (JOBQUEUE) ==============
async def weekly_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Tani waxaa loo yeeraa automatic every Monday"""
    students = load_students()
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
    # Build application
    application = Application.builder().token(BOT_TOKEN).build()

    # Callback handlers
    application.add_handler(CallbackQueryHandler(show_schedule, pattern="^schedule$"))
    application.add_handler(CallbackQueryHandler(show_current_week, pattern="^current_week$"))
    application.add_handler(CallbackQueryHandler(my_progress, pattern="^my_progress$"))
    application.add_handler(CallbackQueryHandler(complete_lesson, pattern="^complete_"))
    application.add_handler(CallbackQueryHandler(next_week, pattern="^next_week$"))
    application.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(settings, pattern="^settings$"))
    application.add_handler(CallbackQueryHandler(toggle_reminders, pattern="^toggle_reminders$"))
    application.add_handler(CallbackQueryHandler(help_cmd, pattern="^help$"))

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", cmd_schedule))
    application.add_handler(CommandHandler("week", cmd_week))
    application.add_handler(CommandHandler("progress", cmd_progress))
    application.add_handler(CommandHandler("next", cmd_next))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("stats", admin_stats))

    # Weekly reminder job (Maalinta Isniinta, 09:00)
    job_queue = application.job_queue
    job_queue.run_repeating(weekly_reminder, interval=timedelta(days=7), first=datetime.strptime("2026-07-21 09:00:00", "%Y-%m-%d %H:%M:%S"))

    # Run the bot until the user presses Ctrl-C
    print("🤖 Bot waa la shidlay... Macallin Bot is working!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
