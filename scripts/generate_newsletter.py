import os
import json
import datetime
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

MODEL = os.getenv("GENERATION_MODEL", "gemini/gemini-2.5-flash")

NEWSLETTER_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>نشرة الذكاء الاصطناعي الأسبوعية</title>
</head>
<body style="font-family: sans-serif; background-color: #020617; color: #ffffff; padding: 20px; direction: rtl; text-align: right;">
    <div style="max-w: 600px; margin: 0 auto; background-color: #0f172a; padding: 30px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
        <h1 style="color: #338dff; font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #1e293b; padding-bottom: 10px;">أسبوع الذكاء الاصطناعي 🚀</h1>
        
        <p style="color: #cbd5e1; font-size: 16px; line-height: 1.6;">مرحباً بك في العدد الأسبوعي من نشرة الذكاء الاصطناعي العربية.</p>
        
        <div style="margin: 25px 0; padding: 20px; background-color: rgba(255,255,255,0.02); border-radius: 8px; border-inline-start: 4px solid #338dff;">
            <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">💡 نصيحة الأسبوع التقنية</h2>
            <p style="color: #e2e8f0; font-size: 14px; line-height: 1.6;">{tip_content}</p>
        </div>

        <h2 style="color: #ffffff; font-size: 18px;">🔥 دورة جديدة متاحة الآن</h2>
        <div style="margin-bottom: 30px; padding: 20px; background-color: rgba(51,141,255,0.05); border-radius: 8px; border: 1px solid rgba(51,141,255,0.1);">
            <h3 style="color: #338dff; font-size: 16px; margin-top: 0;">{course_title}</h3>
            <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin-bottom: 15px;">{course_description}</p>
            <a href="{course_url}" style="display: inline-block; padding: 10px 20px; background-color: #1b6ff5; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">ابدأ الوحدة الأولى مجاناً</a>
        </div>

        <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 40px; border-top: 1px solid #1e293b; padding-top: 20px;">
            تصلك هذه النشرة لأنك اشتركت في منصة الذكاء الاصطناعي العربية.<br>
            <a href="#" style="color: #ef4444; text-decoration: none;">إلغاء الاشتراك</a>
        </p>
    </div>
</body>
</html>
"""

def generate_weekly_newsletter():
    print(f"📧 Generating weekly newsletter issue using model: {MODEL}...")
    try:
        # Load courses catalog to feature the latest course
        courses_index = "site/courses/_index.json"
        latest_course = {
            "title": "بناء أنظمة الوكلاء المتعددة باستخدام LangGraph",
            "description": "تعلم كيفية بناء أنظمة وكلاء ذكية متعددة تتعاون وتنسق مع بعضها لحل المهام المعقدة باستخدام LangGraph.",
            "slug": "langgraph-multi-agents"
        }
        
        if os.path.exists(courses_index):
            with open(courses_index, "r", encoding="utf-8") as f:
                courses = json.load(f)
                if courses:
                    latest_course = courses[0] # Grab the first (newest) one

        # Ask LLM for a technical tip of the week in Arabic
        prompt = "Write a highly practical, 150-word technical tip or bite-sized tutorial in Fusha Arabic about LLMs, prompt engineering, or production ML development. Focus on practical insights for software engineers. No introductory fluff."
        response = completion(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        tip_content = response.choices[0].message.content
        
        # Build HTML
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        course_url = f"https://airankone.com/courses/{latest_course['slug']}/"
        
        html_newsletter = NEWSLETTER_TEMPLATE.format(
            tip_content=tip_content.replace("\n", "<br>"),
            course_title=latest_course["title"],
            course_description=latest_course["description"],
            course_url=course_url
        )
        
        os.makedirs("newsletter/issues", exist_ok=True)
        filename = f"newsletter/issues/{date_str}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_newsletter)
            
        print(f"✅ Generated weekly newsletter issue saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to generate newsletter: {e}")
        return None

if __name__ == "__main__":
    generate_weekly_newsletter()
