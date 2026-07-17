import json
from datetime import datetime, timedelta

COURSES = [
    {
        "id": 1,
        "name": "KOORSADA 1: 40 CASHAR AI (YouTube)",
        "type": "youtube",
        "lessons": [
            {"number": 1, "title": "Chatbot Aasaaska", "link": "https://www.youtube.com/watch?v=zVwhZ9jH0qY"},
            {"number": 2, "title": "Chatbots Noocyada", "link": "https://www.youtube.com/watch?v=dkMO_-Sa1EY"},
            {"number": 3, "title": "Knowledge Base Pipeline", "link": "https://www.youtube.com/watch?v=E4nxnDdsPT8"},
            {"number": 4, "title": "ManyChat Bilow", "link": "https://www.youtube.com/watch?v=FlaqS831-nM"},
            {"number": 5, "title": "Bot Macallin Xisaab", "link": "https://www.youtube.com/watch?v=sbczVS6MDWI"},
            {"number": 6, "title": "ManyChat Hordhac", "link": "https://www.youtube.com/watch?v=y03ckrI0ezc"},
            {"number": 7, "title": "Knowledge Base Manus AI", "link": "https://www.youtube.com/watch?v=r_aHgos0dZg"},
            {"number": 8, "title": "Prompt Heer Sare", "link": "https://www.youtube.com/watch?v=60JgZXi930k"},
            {"number": 9, "title": "Prompts Customization", "link": "https://www.youtube.com/watch?v=I2j7AArFIGQ"},
            {"number": 10, "title": "Comet AI Browser", "link": "https://www.youtube.com/watch?v=R0xhBLqj6ys"},
            {"number": 11, "title": "Manus AI Shaqo Fudud", "link": "https://www.youtube.com/watch?v=0S6ArHPgpCA"},
            {"number": 12, "title": "Paal AI Telegram Bot", "link": "https://www.youtube.com/watch?v=SEfx-QRnJsU"},
            {"number": 13, "title": "Paal AI Part 2", "link": "https://www.youtube.com/watch?v=Jc6ct8O1zLw"},
            {"number": 14, "title": "YouMind AI Waxbarasho", "link": "https://www.youtube.com/watch?v=who5zXdmohA"},
            {"number": 15, "title": "WhatsApp vs Telegram Bot", "link": "https://www.youtube.com/watch?v=N6Gu_mHetIc"},
            {"number": 16, "title": "Custom ChatGPT", "link": "https://www.youtube.com/watch?v=aXrrjehQgh0"},
            {"number": 17, "title": "Prompt Instructions", "link": "https://www.youtube.com/watch?v=dnqFGfKLb4Y"},
            {"number": 18, "title": "Gemini GEMS AI", "link": "https://www.youtube.com/watch?v=vaEaWf1-VWU"},
            {"number": 19, "title": "Perplexity AI Mobile", "link": "https://www.youtube.com/watch?v=EUvNqeLF0AA"},
            {"number": 20, "title": "AI Quiz Tool", "link": "https://www.youtube.com/watch?v=XlopdHYs2aI"},
            {"number": 21, "title": "ManyChat 3", "link": "https://www.youtube.com/watch?v=L9WwTphvuYU"},
            {"number": 22, "title": "FB Messenger Bot", "link": "https://www.youtube.com/watch?v=2IFflSsAzys"},
            {"number": 23, "title": "Messenger Customer Service", "link": "https://www.youtube.com/watch?v=On6q9Xc0--Q"},
            {"number": 24, "title": "Botpress Knowledge Base", "link": "https://www.youtube.com/watch?v=mNLJ-8dZwvg"},
            {"number": 25, "title": "WhatsApp Telegram Marketing", "link": "https://www.youtube.com/watch?v=5Lu9jcaP220"},
            {"number": 26, "title": "Canva AI Sawirro", "link": "https://www.youtube.com/watch?v=5tEtbYLetkU"},
            {"number": 27, "title": "AI Sawir Samee", "link": "https://www.youtube.com/watch?v=wu4oubHInMY"},
            {"number": 28, "title": "VEO 3 Google Video AI", "link": "https://www.youtube.com/watch?v=JBDMbL8VzGo"},
            {"number": 29, "title": "Quiz DeepSeek Telegram", "link": "https://www.youtube.com/watch?v=mGxS8tw-fUc"},
            {"number": 30, "title": "Monica AI Af-Soomaali", "link": "https://www.youtube.com/watch?v=RHq7027Y4U4"},
            {"number": 31, "title": "Telegram Bot A to Z", "link": "https://www.youtube.com/watch?v=TwKLnqnjxsQ"},
            {"number": 32, "title": "Google Bard vs Meta AI", "link": "https://www.youtube.com/watch?v=bFtgqnhEX88"},
            {"number": 33, "title": "Offline AI Apps", "link": "https://www.youtube.com/watch?v=Pn1kU1et7oI"},
            {"number": 34, "title": "WhatsApp 2025", "link": "https://www.youtube.com/watch?v=aJFGVD5vilM"},
            {"number": 35, "title": "Linux Hordhac", "link": "https://www.youtube.com/watch?v=I2F1-5dk3hQ"},
            {"number": 36, "title": "Linux ku Soo Dag", "link": "https://www.youtube.com/watch?v=7K4aibOiPQ4"},
            {"number": 37, "title": "Apps Internet Security", "link": "https://www.youtube.com/watch?v=_RWyy40XfM0"},
            {"number": 38, "title": "AI Video Editing Somalia", "link": "https://www.youtube.com/watch?v=7MB2xCbLt1M"},
            {"number": 39, "title": "Thumbnail Professional", "link": "https://www.youtube.com/watch?v=R2g7f5kXpI0"},
            {"number": 40, "title": "AI Photo Animation", "link": "https://www.youtube.com/watch?v=M9m-dIe46qM"},
        ]
    },
    {
        "id": 2,
        "name": "KOORSADA 2: AI Video Editing (Loom)",
        "type": "loom",
        "lessons": [
            {"number": 1, "title": "InVideo Fundamentals", "link": "https://www.loom.com/share/8465169f3ed34080a9223c7dd8cafb37"},
            {"number": 2, "title": "InVideo – Creating Video from Text", "link": "https://www.loom.com/share/77792231bc8140008e8eeaab77b3d788"},
            {"number": 3, "title": "Pictory.ai Introduction", "link": "https://www.loom.com/share/a63c2b5554274df2a7e97975851834ef"},
            {"number": 4, "title": "Pictory Professional Editing Techniques", "link": "https://www.loom.com/share/5df200096f084354bfd41ca0551edf2f"},
            {"number": 5, "title": "Pictory.ai – AI-Powered Video Editing", "link": "https://www.loom.com/share/f03cfff5dc0a4222842ba074b123ab39"},
            {"number": 6, "title": "Lumen5 – Utilizing Ready-made Templates", "link": "https://www.loom.com/share/1f638be8ca1a4c5a8a110921803e54bd"},
            {"number": 7, "title": "Lumen5 Editing Interface", "link": "https://www.loom.com/share/b7c491c56fff4926a2cdc8a92730e9f0"},
            {"number": 8, "title": "Lumen5 – Audio and Visual Enhancements", "link": "https://www.loom.com/share/42b2100320884386ada6af388c9e6495"},
            {"number": 9, "title": "Audio Refinement and Cutting – Lumen5", "link": "https://www.loom.com/share/1e44a27acab9467582d965fa4c9bb4a1"},
            {"number": 10, "title": "Additional Resources (PDF & Substack)", "link": "https://open.substack.com/pub/mfaratoon/p/9-cashar-ai-video-editing"},
        ]
    },
    {
        "id": 3,
        "name": "KOORSADA 3: Dropshipping iyo Zendrop AI",
        "type": "loom",
        "lessons": [
            {"number": 1, "title": "MAXAA KU DOORNAY ZENDROP", "link": "https://www.loom.com/share/a5f8d34a8bac4bd9be5d0c4b159286cd"},
            {"number": 2, "title": "Zendrop AI Iyo Dropshippingka", "link": "https://www.loom.com/share/9f2291c7056e45beae291b2505caf496"},
            {"number": 3, "title": "Sida Loo Sameeyo Telegama AI Advanced ah", "link": "https://www.loom.com/share/6c78f630461d4fccb835f072e5edbfe1"},
            {"number": 4, "title": "AI Dropshipping Sida Hawsha u Fududeeyey", "link": "https://www.loom.com/share/27c48641a1ed42c084b2d637501ff409"},
            {"number": 5, "title": "Sida Loogu Shubo Appka Zendrop", "link": "https://www.loom.com/share/0ac9d7cd352b462292a42e657fe0668d"},
            {"number": 6, "title": "QAABKA AI SHAQADA U FUDUDEEYEY", "link": "https://www.loom.com/share/96535223749b4347919003b77b1765af"},
            {"number": 7, "title": "ISKU XIDHKA HALKII AAN KA SOO BILOWNAY NO TECH", "link": "https://www.loom.com/share/9913a2b3c4f84de0bc874a69e21fb921"},
            {"number": 8, "title": "DULMAR GUUD OO KU SAABSAN WAXAA BARANAY", "link": "https://www.loom.com/share/600f81758476491bbbbbc4e8518fc9d5"},
            {"number": 9, "title": "ADEEGYADA UGU DAMBEYEY EE DROPSHIPPING", "link": "https://www.loom.com/share/0b5a69dbae8249f38c71b0146645ee77"},
            {"number": 10, "title": "DHAMAYSTIRE GUUD - SIDA HAWSHA AI INOOGU DHAMEEYEY", "link": "https://www.loom.com/share/21ed0c84d67c425cb4aa9a0636c233fd"},
        ]
    },
    {
        "id": 4,
        "name": "KOORSADA 4: ILOODHEERAAD IYO BULSHO",
        "type": "resources",
        "lessons": [
            {"number": 1, "title": "WhatsApp Group (Quiz & Support)", "link": "https://chat.whatsapp.com/BRk1xgsg4ohKAaWN7oDRIe"},
            {"number": 2, "title": "Telegram Channel (Updates & Files)", "link": "https://t.me/+eJxxMKtunMcwODhk"},
            {"number": 3, "title": "Free AI Channel (AI Tools & Tips)", "link": "https://t.me/Farsamada"},
            {"number": 4, "title": "AI-Chatbot Learning WhatsApp", "link": "https://chat.whatsapp.com/KzkcjwraeYhCsUXaexgNyM"},
            {"number": 5, "title": "AI Video Editing WhatsApp", "link": "https://chat.whatsapp.com/G9phNqLyJ3L2RV4lprLUb7"},
            {"number": 6, "title": "AI Automation WhatsApp", "link": "https://chat.whatsapp.com/BRk1xgsg4ohKAaWN7oDRIe"},
            {"number": 7, "title": "YouTube Channel", "link": "https://m.youtube.com/user/MrFaraton"},
            {"number": 8, "title": "Facebook Community", "link": "https://www.facebook.com/soomaalipodcast"},
            {"number": 9, "title": "Substack (Blog)", "link": "https://mfaratoon.substack.com/"},
            {"number": 10, "title": "Course Page", "link": "https://mfaratoon-nebvh2nc.manus.space/course"},
        ]
    }
]

LESSONS_PER_WEEK = 5  # Tusaale ahaan: 5 cashar usbuucii

def generate_schedule(start_date=None):
    if start_date is None:
        start_date = datetime.now().date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    schedule = []
    current_week = 1
    lesson_counter = 0

    all_lessons = []
    for course in COURSES:
        for lesson in course["lessons"]:
            all_lessons.append({
                "course_id": course["id"],
                "course_name": course["name"],
                "type": course["type"],
                "lesson_number": lesson["number"],
                "title": lesson["title"],
                "link": lesson["link"],
            })

    week_start = start_date
    week_lessons = []

    for idx, lesson in enumerate(all_lessons, 1):
        week_lessons.append(lesson)
        lesson_counter += 1

        if lesson_counter % LESSONS_PER_WEEK == 0 or idx == len(all_lessons):
            week_end = week_start + timedelta(days=6)
            schedule.append({
                "week": current_week,
                "start_date": str(week_start),
                "end_date": str(week_end),
                "lessons": week_lessons.copy()
            })
            week_lessons = []
            current_week += 1
            week_start = week_end + timedelta(days=1)

    return schedule

def save_schedule_csv(schedule, filename="teacher_schedule.csv"):
    import csv
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Week", "Start Date", "End Date", "Course", "Lesson #", "Title", "Link", "Type"])
        for week in schedule:
            for lesson in week["lessons"]:
                writer.writerow([
                    week["week"],
                    week["start_date"],
                    week["end_date"],
                    lesson["course_name"],
                    lesson["lesson_number"],
                    lesson["title"],
                    lesson["link"],
                    lesson["type"]
                ])
    print(f"Schedule saved to {filename}")

if __name__ == "__main__":
    schedule = generate_schedule("2026-07-21")  # Tusaale: usbuuca dambe
    save_schedule_csv(schedule)
    print(f"Wadarta usbuucyada: {len(schedule)}")
    print(f"Wadarta casharada: {sum(len(w['lessons']) for w in schedule)}")
