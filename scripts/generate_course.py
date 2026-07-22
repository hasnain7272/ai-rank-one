import os, json, csv, sys
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("GENERATION_MODEL", "gemini/gemini-2.5-pro")
QUEUE_FILE = "content-queue.csv"

PROMPT = """You are a senior AI engineer. Write a 5-module course in Arabic on: "{topic}".
Return ONLY a JSON object (no markdown):
{{
  "title": "Arabic Title", "description": "Arabic Summary", "tags": ["Tag1", "Tag2"],
  "price": 39, "duration": "5 hours", "gradient": "from-brand-500 to-blue-500",
  "modules": [
    {{"title": "Module 1", "content": "Markdown intro content"}},
    {{"title": "Module 2", "content": "Gated content"}},
    {{"title": "Module 3", "content": "Gated content"}},
    {{"title": "Module 4", "content": "Gated content"}},
    {{"title": "Module 5", "content": "Gated content"}}
  ]
}}"""

def generate_course(topic):
    key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key and "your_" not in key:
        try:
            res = completion(model=MODEL, messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": PROMPT.format(topic=topic)}], response_format={"type": "json_object"})
            return json.loads(res.choices[0].message.content)
        except Exception as e: print(f"API Error: {e}")
    return {
        "title": f"دورة متقدمة في {topic}", "description": f"دورة عملية متقدمة في {topic}.",
        "tags": [topic.split()[0], "AI", "Python"], "price": 39, "duration": "5 ساعات", "gradient": "from-brand-500 to-indigo-500",
        "modules": [{"title": f"الوحدة {i+1}: {topic}", "content": f"# الوحدة {i+1}\nمحتوى تفصيلي لـ {topic}."} for i in range(5)]
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        t = sys.argv[1]
        slug = t.lower().replace(" ", "-").replace(":", "")
        os.makedirs("site/courses", exist_ok=True)
        with open(f"site/courses/{slug}.json", "w", encoding="utf-8") as f: json.dump(generate_course(t), f, ensure_ascii=False, indent=2)
        print(f"Generated site/courses/{slug}.json")
    else:
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f: csv.writer(f).writerows([["Topic", "Status"], ["LangGraph Multi Agents", "pending"]])
            sys.exit(0)
        rows, updated = [], False
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            r = csv.reader(f)
            rows.append(next(r))
            for row in r:
                if len(row) >= 2 and row[1] == "pending" and not updated:
                    t = row[0]
                    slug = t.lower().replace(" ", "-").replace(":", "")
                    os.makedirs("site/courses", exist_ok=True)
                    with open(f"site/courses/{slug}.json", "w", encoding="utf-8") as f: json.dump(generate_course(t), f, ensure_ascii=False, indent=2)
                    row[1], updated = "completed", True
                rows.append(row)
        if updated:
            with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f: csv.writer(f).writerows(rows)
            print("Queue updated.")
