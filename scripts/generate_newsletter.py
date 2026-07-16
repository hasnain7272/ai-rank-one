import os
import datetime

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
            <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">💡 نصيحة الأسبوع التقنية: إدارة الذاكرة في LangGraph</h2>
            <p style="color: #e2e8f0; font-size: 14px; line-height: 1.6;">
                عند بناء أنظمة الوكلاء المتعددة (Multi-Agents)، فإن التحدي الأكبر هو الحفاظ على سياق المحادثة عبر الجلسات المختلفة.<br><br>
                باستخدام LangGraph، يمكنك إعداد ذاكرة مستمرة للجلسات بسهولة عبر استخدام `SqliteSaver` محلياً أو `PostgresSaver` في بيئة الإنتاج. يتيح ذلك للوكلاء تذكر التفاعلات السابقة لكل مستخدم بناءً على معرف فريد `thread_id` دون الحاجة لإعادة تمرير التاريخ بالكامل يدوياً.<br><br>
                <code>config = {{"configurable": {{"thread_id": "user-session-123"}}}}</code>
            </p>
        </div>

        <h2 style="color: #ffffff; font-size: 18px;">🔥 دورة جديدة متاحة الآن</h2>
        <div style="margin-bottom: 30px; padding: 20px; background-color: rgba(51,141,255,0.05); border-radius: 8px; border: 1px solid rgba(51,141,255,0.1);">
            <h3 style="color: #338dff; font-size: 16px; margin-top: 0;">بناء أنظمة الوكلاء المتعددة باستخدام LangGraph</h3>
            <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin-bottom: 15px;">
                تعلم كيفية بناء أنظمة وكلاء ذكية متعددة تتعاون وتنسق مع بعضها لحل المهام المعقدة باستخدام LangGraph.
            </p>
            <a href="https://airankone.com/courses/langgraph-multi-agents/" style="display: inline-block; padding: 10px 20px; background-color: #1b6ff5; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">ابدأ الوحدة الأولى مجاناً</a>
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
    print("📧 Generating weekly newsletter issue...")
    try:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        
        os.makedirs("newsletter/issues", exist_ok=True)
        filename = f"newsletter/issues/{date_str}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(NEWSLETTER_TEMPLATE)
            
        print(f"✅ Generated weekly newsletter issue saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to generate newsletter: {e}")
        return None

if __name__ == "__main__":
    generate_weekly_newsletter()
