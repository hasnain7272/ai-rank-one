import os
import json
import csv
import sys
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# Config
MODEL = os.getenv("GENERATION_MODEL", "gemini/gemini-2.5-pro")
QUEUE_FILE = "content-queue.csv"

GENERATION_PROMPT = """You are a senior AI/ML engineer and expert instructor.
Write a comprehensive, technically rigorous 5-module course in Fusha Arabic on the topic: "{topic}".

Guidelines:
1. Target audience: Production-level AI developers and engineers.
2. Tone: Professional, academic, and highly technical. Never use translated-English phrasing that feels unnatural in Arabic. Use standardized technical terms (e.g., الاسترجاع المعزز بالتوليد for RAG).
3. Include deep code snippets in Python, command line examples, and clear architectural ASCII diagrams.
4. Put Arabic code comments to explain complex operations.

You must return ONLY a JSON object (no markdown wrapping, no extra text) with the following structure:
{{
  "title": "Arabic Title of the Course",
  "description": "Short Arabic summary of what this course covers",
  "tags": ["Tag1", "Tag2", "Tag3"],
  "price": 29,
  "duration": "Duration (e.g., 4 ساعات)",
  "gradient": "from-brand-500 to-blue-500", -- tailwind gradient classes
  "modules": [
    {{
      "title": "Module 1: Title of Introduction",
      "content": "Markdown Content of Module 1 (The Free Module, very detailed, introductory concepts, code setups, 1500+ words)"
    }},
    {{
      "title": "Module 2: Advanced Concept 1",
      "content": "Markdown Content of Module 2 (Gated, deep-dive implementation, math/theory, code)"
    }},
    {{
      "title": "Module 3: Advanced Concept 2",
      "content": "Markdown Content of Module 3 (Gated, production configuration, bottlenecks, code)"
    }},
    {{
      "title": "Module 4: Practical Project/Lab",
      "content": "Markdown Content of Module 4 (Gated, full end-to-end Python file and architectural walk-through)"
    }},
    {{
      "title": "Module 5: Production Concerns & Gotchas",
      "content": "Markdown Content of Module 5 (Gated, monitoring, costs, common gotchas, and conclusions)"
    }}
  ]
}}
"""

def generate_course(topic):
    print(f"🧠 Generating course for topic: {topic} using model: {MODEL}...")
    
    # Check if API key is configured
    api_key_set = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if api_key_set and "your_" not in api_key_set:
        try:
            response = completion(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a specialized JSON generator. You output only valid JSON."},
                    {"role": "user", "content": GENERATION_PROMPT.format(topic=topic)}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"❌ Generation API call failed: {e}")
            print("⚠️ Falling back to local template generator...")
            
    # Local fallback template generator
    return {
        "title": f"دورة متقدمة في {topic}",
        "description": f"دورة عملية متقدمة مصممة لمهندسي البرمجيات العرب لتغطية أساسيات وتطبيقات {topic} في بيئات العمل الفعلية.",
        "tags": [topic.split()[0] if topic.split() else "AI", "Python", "Mute"],
        "price": 29,
        "duration": "4 ساعات",
        "gradient": "from-brand-500 to-indigo-500",
        "modules": [
            {
                "title": "الوحدة 1: المقدمة والمفاهيم الأساسية",
                "content": f"# مقدمة في {topic}\n\nنظرة عامة على المفاهيم والركائز الأساسية لـ {topic} وكيفية إعداد البيئة البرمجية للعمل.\n\n## الأساسيات:\n- فهم المشكلة التي يحلها هذا المفهوم.\n- البنية الهندسية العامة.\n\n```python\n# إعداد أولي لبدء العمل\ndef init_model():\n    print('تهيئة نظام {topic}...')\n    return True\n```"
            },
            {
                "title": "الوحدة 2: الهيكل الهندسي والتصميم المتقدم",
                "content": f"# الهيكل الهندسي والتصميم المتقدم لـ {topic}\n\nشرح تفصيلي لتصميم وهيكلة الحلول البرمجية بالاعتماد على أفضل الممارسات التقنية."
            },
            {
                "title": "الوحدة 3: التحديات والمشاكل وحلولها",
                "content": f"# التحديات والمشاكل وحلولها\n\nكيفية التعامل مع الأخطاء الشائعة وحل المشكلات المتعلقة بالأداء وتخفيض زمن الاستجابة."
            },
            {
                "title": "الوحدة 4: مشروع عملي تطبيقي متكامل",
                "content": f"# مشروع عملي تطبيقي متكامل لـ {topic}\n\nخطوات بناء مشروع كامل مع الكود البرمجي وشرح مفصل لربط الأجزاء ببعضها."
            },
            {
                "title": "الوحدة 5: النشر والتشغيل والمراقبة في الإنتاج",
                "content": f"# النشر والتشغيل والمراقبة في بيئة الإنتاج\n\nكيفية تغليف الكود ونشره على السحابة ومراقبة الأداء لضمان الكفاءة والدقة المستمرة."
            }
        ]
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run directly for a single topic
        topic = sys.argv[1]
        course_data = generate_course(topic)
        if course_data:
            slug = topic.lower().replace(" ", "-").replace(":", "").replace("/", "")
            with open(f"site/courses/{slug}.json", "w", encoding="utf-8") as f:
                json.dump(course_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Generated course file: site/courses/{slug}.json")
    else:
        # Run through queue
        if not os.path.exists(QUEUE_FILE):
            print("QUEUE_FILE not found. Creating a blank content-queue.csv...")
            with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Topic", "Status"])
                writer.writerow(["LangGraph Multi Agents", "pending"])
            sys.exit(0)
            
        rows = []
        updated = False
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows.append(header)
            for row in reader:
                if len(row) < 2: continue
                topic, status = row[0], row[1]
                if status == "pending" and not updated:
                    course_data = generate_course(topic)
                    if course_data:
                        slug = topic.lower().replace(" ", "-").replace(":", "").replace("/", "")
                        os.makedirs("site/courses", exist_ok=True)
                        with open(f"site/courses/{slug}.json", "w", encoding="utf-8") as f:
                            json.dump(course_data, f, ensure_ascii=False, indent=2)
                        row[1] = "completed"
                        updated = True
                rows.append(row)
                
        if updated:
            with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            print("✅ Queue updated.")
        else:
            print("📭 No pending topics in queue.")
