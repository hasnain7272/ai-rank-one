import os
import json
import sys
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

MODEL = os.getenv("GENERATION_MODEL", "gemini/gemini-2.5-flash")

SOCIAL_PROMPT = """You are a master technical content marketer who writes viral tech posts in Arabic.
Read the following course details and generate a complete suite of marketing copy in Fusha Arabic.

Course Title: {title}
Description: {description}
Module 1 (Free Teaser) Summary:
{module1_content}

Your output must be a single JSON object containing:
{{
  "twitter": [
    {{
      "title": "Thread 1: Course Launch (3-5 tweets)",
      "content": "Tweet 1: ...\\n\\nTweet 2: ...\\n\\nTweet 3: ..."
    }},
    {{
      "title": "Thread 2: Technical Deep-Dive / Teaser (3-5 tweets)",
      "content": "Tweet 1: ...\\n\\nTweet 2: ...\\n\\nTweet 3: ..."
    }}
  ],
  "linkedin": [
    {{
      "title": "Post 1: Professional Announcement",
      "content": "LinkedIn Post Content (focused on professional growth, upskilling, and how it helps careers)"
    }},
    {{
      "title": "Post 2: Insight / Key Takeaway",
      "content": "LinkedIn Post Content (focused on a specific technical challenge solved in the course)"
    }}
  ],
  "youtube": {{
    "title": "5-Minute YouTube Script & Assets",
    "script": "Narrator: ...\\n[Show Slide: ...]\\nNarrator: ...",
    "description": "Video description with timestamps and links",
    "thumbnail_prompt": "Image generation prompt for the video thumbnail"
  }}
}}

Make sure all content is engaging, native Fusha Arabic, and includes relevant hashtags like #الذكاء_الاصطناعي #برمجة #بايثون.
Return ONLY the raw JSON object (no markdown formatting, no comments).
"""

def generate_social(course_filepath):
    print(f"📣 Generating social media assets for {course_filepath} using model: {MODEL}...")
    try:
        with open(course_filepath, "r", encoding="utf-8") as f:
            course_data = json.load(f)
            
        title = course_data.get("title", "")
        description = course_data.get("description", "")
        # Grab first module's content (teaser)
        module1 = course_data.get("modules", [{}])[0]
        module1_content = module1.get("content", "")[:3000] # Cap to avoid token bloat
        
        response = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a marketing JSON generator. You output only valid JSON."},
                {"role": "user", "content": SOCIAL_PROMPT.format(title=title, description=description, module1_content=module1_content)}
            ],
            response_format={"type": "json_object"}
        )
        
        social_data = json.loads(response.choices[0].message.content)
        
        # Save output in organized folders
        slug = course_data.get("slug") or os.path.basename(course_filepath).replace(".json", "")
        output_dir = f"social/{slug}"
        os.makedirs(f"{output_dir}/twitter", exist_ok=True)
        os.makedirs(f"{output_dir}/linkedin", exist_ok=True)
        os.makedirs(f"{output_dir}/youtube", exist_ok=True)
        
        # Save Twitter
        for idx, thread in enumerate(social_data.get("twitter", [])):
            with open(f"{output_dir}/twitter/thread_{idx+1}.md", "w", encoding="utf-8") as f:
                f.write(thread.get("content", ""))
                
        # Save LinkedIn
        for idx, post in enumerate(social_data.get("linkedin", [])):
            with open(f"{output_dir}/linkedin/post_{idx+1}.md", "w", encoding="utf-8") as f:
                f.write(post.get("content", ""))
                
        # Save YouTube
        yt = social_data.get("youtube", {})
        with open(f"{output_dir}/youtube/script.md", "w", encoding="utf-8") as f:
            f.write(f"# Script\n\n{yt.get('script', '')}\n\n# Description\n\n{yt.get('description', '')}")
        with open(f"{output_dir}/youtube/thumbnail_prompt.txt", "w", encoding="utf-8") as f:
            f.write(yt.get("thumbnail_prompt", ""))
            
        # Create schedule file
        schedule = {
            "course": slug,
            "posts": [
                {"file": "thread_1.md", "platform": "twitter", "offset_days": 1},
                {"file": "post_1.md", "platform": "linkedin", "offset_days": 1},
                {"file": "thread_2.md", "platform": "twitter", "offset_days": 3},
                {"file": "post_2.md", "platform": "linkedin", "offset_days": 5}
            ]
        }
        with open(f"{output_dir}/schedule.json", "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2)
            
        print(f"✅ Generated marketing assets in {output_dir}/")
        return True
    except Exception as e:
        print(f"❌ Failed to generate social assets: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_social(sys.argv[1])
    else:
        print("Usage: python generate_social.py <path_to_course_json>")
