import os
import json
import sys
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

SITE_URL = os.getenv("SITE_URL", "https://ai-rank-one.hasnainrazalakhani7272.workers.dev").rstrip("/")
DEAD_DOMAIN = "https://airankone.com"

COURSES_SOCIAL = {
    "langgraph-multi-agents": {
        "twitter": [
            "🚀 دورة جديدة: بناء أنظمة الوكلاء المتعددة (Multi-Agents) باستخدام LangGraph.\n\nلماذا تعتمد على نموذج لغوي واحد للقيام بكل شيء بينما يمكنك بناء فريق عمل كامل من الوكلاء المتخصصين؟\n\nفي هذه السلسلة سنبني معاً أنظمة تفاعلية قادرة على التنسيق والتعاون وحل المشكلات المعقدة.\n\nتابع الثريد 👇 #الذكاء_الاصطناعي #برمجة",
            "1/5 الفكرة الأساسية في أنظمة الوكلاء المتعددة هي التخصص.\n\nبدلاً من إعطاء أمر ضخم لنموذج واحد، نقوم بتقسيم المهمة:\n- وكيل للبحث في الإنترنت 🔍\n- وكيل لكتابة الكود البرمجي 💻\n- وكيل لمراجعة الكود واكتشاف الأخطاء 🛡️\n\nكل وكيل يعمل بشكل منفصل وينسق مع بقية الفريق.",
            "2/5 نستخدم LangGraph لأنها تتيح لنا تمثيل تدفق العمل كرسم بياني (Graph):\n- العقد (Nodes): تمثل الوكلاء أو العمليات.\n- الحواف (Edges): تمثل اتجاه تدفق البيانات والشروط الانتقالية.\n\nهذا يمنحنا تحكماً كاملاً بالدورة البرمجية مقارنة بالأطر التقليدية.",
            "3/5 إليك كود بسيط لتعريف حالة مشتركة (State) بين الوكلاء:\n\n```python\nfrom typing import Annotated, TypedDict\nfrom langgraph.graph.message import add_messages\n\nclass State(TypedDict):\n    messages: Annotated[list, add_messages]\n```\n\nهذه الحالة تحفظ كافة الحوارات وتنسقها تلقائياً.",
            "4/5 جرب الوحدة الأولى بالكامل مجاناً الآن على موقعنا! تعلم كيف تبني وتدير بيئة عمل الوكلاء بنفسك مع مشاريع عملية كاملة.\n\n🔗 تفضل بالزيارة: https://airankone.com/courses/langgraph-multi-agents"
        ],
        "linkedin": [
            "🚀 يسعدني الإعلان عن إطلاق دورة جديدة بالكامل: 'بناء أنظمة الوكلاء المتعددة (Multi-Agents) باستخدام LangGraph' باللغة العربية الفصحى للمطورين ومهندسي الذكاء الاصطناعي.\n\nفي بيئات العمل الحقيقية، لا يمكننا الاعتماد على نموذج لغوي واحد (Single LLM) للقيام بمهام متباينة وصعبة. الحل يكمن في تصميم وتطوير وكلاء متعددين متخصصين يعملون كفريق عمل متكامل.\n\nتعلم في هذه الدورة:\n- التخطيط وهيكلة أنظمة الوكلاء (Agentic Planning).\n- إدارة الذاكرة المستمرة وتدفق البيانات.\n- دمج الأدوات الخارجية (Tools) والتحكم بحلقة التكرار (Loops).\n\nالوحدة الأولى متاحة مجاناً بالكامل للتجربة مع الكود البرمجي.\n\n🔗 ابدأ التعلم الآن: https://airankone.com/courses/langgraph-multi-agents\n\n#الذكاء_الاصطناعي #برمجة #بايثون #تعلم_الآلة #مطورين"
        ],
        "youtube": {
            "script": "مرحباً بكم في هذا الدرس العملي. اليوم سنتحدث عن بناء أنظمة الوكلاء المتعددة باستخدام LangGraph.\n\n[عرض الشريحة الأولى: هيكلية الوكلاء]\n\nالهدف هو بناء أنظمة ذكية تتعاون لحل المشكلات المعقدة. سنقوم بتعريف حالة مشتركة ومن ثم كتابة كود مخصص لكل وكيل.\n\n[الانتقال لبيئة التطوير وكتابة الكود]\n\nالآن دعونا نشغل هذا الكود ونشاهد كيف يتعاون وكيل البحث مع وكيل البرمجة وكيف يتم تبادل الرسائل بينهما تلقائياً.",
            "description": "فيديو توضيحي لبناء وكلاء الذكاء الاصطناعي المتعددة باستخدام بايثون ومكتبة LangGraph. ابدأ الدورة الكاملة مجاناً من هنا: https://airankone.com/courses/langgraph-multi-agents",
            "thumbnail_prompt": "A modern 3D render representing connected AI agents collaborating, dark blue background, glowing network nodes, high tech, corporate branding"
        }
    },
    "building-a-production-rag-system": {
        "twitter": [
            "🚀 دورة جديدة: بناء نظام RAG للإنتاج مع البحث الهجين وإعادة الترتيب.\n\nهل تعاني من ضعف إجابات نظام الـ RAG الخاص بك عند التعامل مع مستندات حقيقية وصعبة؟\n\nفي هذه الدورة، سنتعلم الحلول الهندسية التي تستخدمها كبرى الشركات لحل هذه المشكلة.\n\nتابع الثريد 👇 #الذكاء_الاصطناعي #RAG",
            "1/4 البحث المتجهي (Vector Search) وحده لا يكفي في الإنتاج. إذا بحث المستخدم عن رقم تسلسلي دقيق، قد يفشل المتجه الدلالي.\n\nالحل هو البحث الهجين (Hybrid Search) الذي يدمج بين البحث النصي التقليدي (BM25) والبحث المتجهي الكثيف.",
            "2/4 لدمج النتائج نستخدم خوارزمية Reciprocal Rank Fusion (RRF):\n\n```python\ndef rrf(dense_results, sparse_results, k=60):\n    score = {}\n    for rank, doc in enumerate(dense_results):\n        score[doc] = score.get(doc, 0) + 1.0 / (k + rank + 1)\n    return sorted(score.items(), key=lambda x: x[1], reverse=True)\n```",
            "3/4 افتح الوحدة الأولى مجاناً الآن وتعلم تقنيات تقسيم المستندات وتطبيق إعادة الترتيب (Reranking) لتقليل زمن الاستجابة والهلوسة.\n\n🔗 ابدأ الآن: https://airankone.com/courses/building-a-production-rag-system"
        ],
        "linkedin": [
            "🚀 أطلقت للتو دورة: 'بناء نظام RAG للإنتاج مع البحث الهجين وإعادة الترتيب' بالعربية الفصحى.\n\nمن أكبر المشاكل التي تواجه المهندسين عند نقل أنظمة RAG للإنتاج هي دقة وجودة السياق المسترجع. في هذه الدورة العملية، نتجاوز النماذج البسيطة ونبني نظاماً دقيقاً قادراً على التعامل مع ملايين المستندات.\n\nالمحاور:\n- التقسيم الدلالي والذكي للمستندات (Chunking).\n- دمج محركات البحث النصية والمتجهية.\n- تحسين النتائج وتقليل التكلفة بنماذج Rerankers.\n\n🔗 جرب الوحدة الأولى مجاناً: https://airankone.com/courses/building-a-production-rag-system\n\n#الذكاء_الاصطناعي #تعلم_الآلة #RAG #بايثون #مهندسين"
        ],
        "youtube": {
            "script": "مرحباً بكم. اليوم سنقوم ببناء نظام RAG متقدم للإنتاج.\n\n[عرض واجهة البحث الهجين]\n\nسنقوم بدمج استعلامات المتجهات مع استعلامات الكلمات المفتاحية للحصول على أفضل دقة ممكنة.\n\n[عرض الكود الخاص بخوارزمية RRF]\n\nهذه الخوارزمية تضمن لنا ترتيباً دقيقاً للمستندات المسترجعة قبل تمريرها للنموذج اللغوي.",
            "description": "فيديو تطبيقي لبناء نظام RAG حقيقي للشركات مع البحث الهجين وإعادة الترتيب. تفضل بزيارة الدورة كاملة: https://airankone.com/courses/building-a-production-rag-system",
            "thumbnail_prompt": "Data architecture diagram for RAG with hybrid search and reranking, glowing data flows, vector database icon, futuristic tech look"
        }
    }
}

def generate_all_social():
    print("📣 Generating mock pre-written social media assets...")
    for slug, data in COURSES_SOCIAL.items():
        output_dir = f"social/{slug}"
        os.makedirs(f"{output_dir}/twitter", exist_ok=True)
        os.makedirs(f"{output_dir}/linkedin", exist_ok=True)
        os.makedirs(f"{output_dir}/youtube", exist_ok=True)

        def fix(text):
            return text.replace(DEAD_DOMAIN, SITE_URL)

        # Save Twitter Thread
        with open(f"{output_dir}/twitter/thread_1.md", "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(fix(t) for t in data["twitter"]))

        # Save LinkedIn Post
        with open(f"{output_dir}/linkedin/post_1.md", "w", encoding="utf-8") as f:
            f.write(fix(data["linkedin"][0]))

        # Save YouTube script
        yt = data["youtube"]
        with open(f"{output_dir}/youtube/script.md", "w", encoding="utf-8") as f:
            f.write(f"# Script\n\n{fix(yt['script'])}\n\n# Description\n\n{fix(yt['description'])}")
        with open(f"{output_dir}/youtube/thumbnail_prompt.txt", "w", encoding="utf-8") as f:
            f.write(fix(yt["thumbnail_prompt"]))
            
        # Save schedule file
        schedule = {
            "course": slug,
            "posts": [
                {"file": "thread_1.md", "platform": "twitter", "offset_days": 1},
                {"file": "post_1.md", "platform": "linkedin", "offset_days": 1}
            ]
        }
        with open(f"{output_dir}/schedule.json", "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2)
            
        print(f"✅ Pre-populated social assets for: {slug}")

if __name__ == "__main__":
    generate_all_social()
