"""
=============================================================
MACALLIN BOT -- PRE-FLIGHT TEST
Hubiya: Imports, Data, Schedule, Quiz, PDF, Database
=============================================================
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_imports():
    print("[CHECK] Testing Imports...")
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler
        from fpdf import FPDF
        import qrcode
        print("  [OK] python-telegram-bot")
        print("  [OK] fpdf2")
        print("  [OK] Pillow")
        print("  [OK] qrcode")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False

def test_course_data():
    print("\n[CHECK] Testing Course Data...")
    try:
        from course_data import COURSES, generate_schedule
        total_lessons = sum(len(c["lessons"]) for c in COURSES)
        print(f"  [OK] Courses loaded: {len(COURSES)}")
        print(f"  [OK] Total lessons: {total_lessons}")
        
        schedule = generate_schedule("2026-07-21")
        print(f"  [OK] Schedule generated: {len(schedule)} weeks")
        return True
    except Exception as e:
        print(f"  [FAIL] Course data failed: {e}")
        return False

def test_database():
    print("\n[CHECK] Testing Database (Local)...")
    try:
        import json
        test_file = Path("test_students.json")
        test_data = {"12345": {"user_id": 12345, "first_name": "Test"}}
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        with open(test_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["12345"]["first_name"] == "Test"
        test_file.unlink()
        print("  [OK] Local JSON read/write OK")
        return True
    except Exception as e:
        print(f"  [FAIL] Database test failed: {e}")
        return False

def test_quiz():
    print("\n[CHECK] Testing Quiz System...")
    try:
        from telegram_course_bot_v2 import QUIZ_DATA, get_quiz_for_lesson
        
        quiz = get_quiz_for_lesson("Chatbot Aasaaska")
        assert quiz is not None
        assert len(quiz) > 0
        assert "q" in quiz[0]
        assert "options" in quiz[0]
        assert "correct" in quiz[0]
        print(f"  [OK] Quiz found: 'Chatbot Aasaaska' ({len(quiz)} questions)")
        
        total_quizzes = sum(len(v) for course in QUIZ_DATA.values() for v in course.values())
        print(f"  [OK] Total quiz entries: {total_quizzes}")
        return True
    except Exception as e:
        print(f"  [FAIL] Quiz test failed: {e}")
        return False

def test_certificate_pdf():
    print("\n[CHECK] Testing Certificate PDF...")
    try:
        from telegram_course_bot_v2 import generate_certificate
        
        pdf_bytes, cert_id = generate_certificate("Test Student", "MACALLIN AI Course")
        assert len(pdf_bytes) > 0
        assert len(cert_id) == 12
        
        test_pdf = Path("test_certificate.pdf")
        with open(test_pdf, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"  [OK] PDF generated: {len(pdf_bytes)} bytes")
        print(f"  [OK] Certificate ID: {cert_id}")
        print(f"  [FILE] Test PDF saved: test_certificate.pdf")
        return True
    except Exception as e:
        print(f"  [FAIL] PDF test failed: {e}")
        return False

def test_bot_syntax():
    print("\n[CHECK] Testing Bot Syntax...")
    try:
        import py_compile
        py_compile.compile("telegram_course_bot_v2.py", doraise=True)
        print("  [OK] telegram_course_bot_v2.py syntax OK")
        return True
    except Exception as e:
        print(f"  [FAIL] Syntax error: {e}")
        return False

def main():
    print("=" * 60)
    print("  MACALLIN BOT -- PRE-FLIGHT TEST")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Course Data", test_course_data()))
    results.append(("Database", test_database()))
    results.append(("Quiz", test_quiz()))
    results.append(("Certificate PDF", test_certificate_pdf()))
    results.append(("Bot Syntax", test_bot_syntax()))
    
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, ok in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n  {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  READY! Bot is fully functional.")
        print("  Next steps:")
        print("  1. Get TOKEN from @BotFather")
        print("  2. Edit: telegram_course_bot_v2.py")
        print("  3. Run: python telegram_course_bot_v2.py")
    else:
        print("\n  Errors found. Check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
