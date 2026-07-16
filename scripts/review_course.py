import os
import json
import sys
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

REVIEW_MODEL = os.getenv("REVIEW_MODEL", "gemini/gemini-2.5-flash")

REVIEW_PROMPT = """You are an expert native Arabic-speaking senior software architect at KAUST.
Review the following technical AI course JSON for:
1. Arabic grammatical correctness (نحو وصرف).
2. Accurate technical translation (no awkward literal translations).
3. Clear and complete Python/bash code snippets.
4. Correctness of code comments in Arabic.

Return the modified and corrected JSON containing the EXACT same structure as input. Do not change the JSON keys. Fix any issues directly in the text/markdown content.
Only return the valid JSON object (no markdown formatting, no comments outside the JSON).

Course JSON to review:
{course_json}
"""

def review_course(filepath):
    print(f"🧐 Reviewing course: {filepath} using model: {REVIEW_MODEL}...")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            course_data = json.load(f)
            
        response = completion(
            model=REVIEW_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional editor and JSON validator. You output only valid JSON."},
                {"role": "user", "content": REVIEW_PROMPT.format(course_json=json.dumps(course_data, ensure_ascii=False))}
            ],
            response_format={"type": "json_object"}
        )
        
        reviewed_data = json.loads(response.choices[0].message.content)
        
        # Save reviewed version back
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(reviewed_data, f, ensure_ascii=False, indent=2)
            
        print(f"✨ Course review completed. Refined content saved to {filepath}")
        return True
    except Exception as e:
        print(f"⚠️ Review pipeline skipped or failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        review_course(sys.argv[1])
    else:
        print("Usage: python review_course.py <path_to_course_json>")
