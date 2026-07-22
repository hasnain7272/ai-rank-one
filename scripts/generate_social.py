import os, json, sys
from dotenv import load_dotenv
from litellm import completion

if sys.platform == "win32": sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
MODEL = os.getenv("GENERATION_MODEL", "gemini/gemini-2.5-flash")
SITE_URL = os.getenv("SITE_URL", "https://ai-rank-one.hasnainrazalakhani7272.workers.dev").rstrip("/")

PROMPT = """Read course details and write Arabic social posts JSON:
Title: {title} | Description: {description}
JSON structure: {{"twitter":[{"content":"tweet1"}], "linkedin":[{"content":"post1"}], "youtube":{{"script":"s","description":"d","thumbnail_prompt":"p"}}}}"""

def generate_social(filepath):
    print(f"📣 Generating social media assets for {filepath}...")
    try:
        with open(filepath, encoding="utf-8") as f: data = json.load(f)
        title, desc = data.get("title",""), data.get("description","")
        slug = data.get("slug") or os.path.basename(filepath).replace(".json","")
        key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        res_data = None
        if key and "your_" not in key:
            try:
                res = completion(model=MODEL, messages=[{"role":"user","content":PROMPT.format(title=title, description=desc)}], response_format={"type":"json_object"})
                res_data = json.loads(res.choices[0].message.content)
            except Exception as e: print(f"API failed: {e}")
        if not res_data:
            res_data = {
                "twitter": [{"content": f"🚀 دورة جديدة: {title}\n{desc}\n#الذكاء_الاصطناعي"}],
                "linkedin": [{"content": f"🚀 دورة جديدة: {title}\n{desc}\n🔗 {SITE_URL}/courses/{slug}/"}],
                "youtube": {"script": f"شرح دورة {title}", "description": desc, "thumbnail_prompt": f"Course {title}"}
            }
        out = f"social/{slug}"
        for p in ["twitter", "linkedin", "youtube"]: os.makedirs(f"{out}/{p}", exist_ok=True)
        for i, t in enumerate(res_data.get("twitter",[])):
            with open(f"{out}/twitter/thread_{i+1}.md","w",encoding="utf-8") as f: f.write(t.get("content",""))
        for i, p in enumerate(res_data.get("linkedin",[])):
            with open(f"{out}/linkedin/post_{i+1}.md","w",encoding="utf-8") as f: f.write(p.get("content",""))
        yt = res_data.get("youtube",{})
        with open(f"{out}/youtube/script.md","w",encoding="utf-8") as f: f.write(f"# Script\n{yt.get('script','')}\n# Description\n{yt.get('description','')}")
        print(f"✅ Generated marketing assets in {out}/")
        return True
    except Exception as e: print(f"Failed: {e}"); return False

if __name__ == "__main__":
    if len(sys.argv) > 1: generate_social(sys.argv[1])
    else: print("Usage: python generate_social.py <path_to_course_json>")
