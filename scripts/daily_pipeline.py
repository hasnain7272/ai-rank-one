import os
import csv
import subprocess
from dotenv import load_dotenv

load_dotenv()

# We specify python executable inside virtual environment
PYTHON_BIN = os.path.join(".venv", "Scripts", "python") if os.name == "nt" else os.path.join(".venv", "bin", "python")

def run_script(script_name, *args):
    cmd = [PYTHON_BIN, os.path.join("scripts", script_name)] + list(args)
    print(f"🏃 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"❌ Error running {script_name}:\n{result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("🌅 Starting Daily Antigravity Platform Pipeline...")
    
    # 1. Run generation script
    # It reads content-queue.csv and processes any pending course.
    if not run_script("generate_course.py"):
        print("❌ Generation failed. Exiting.")
        return

    # Check for newly generated JSON course files
    courses_dir = "site/courses"
    if not os.path.exists(courses_dir):
        print("📭 No courses folder found.")
        return

    new_courses = []
    # Find JSON files that don't have matching HTML folders compiled yet
    for file in os.listdir(courses_dir):
        if file.endswith(".json") and file != "_index.json":
            slug = file.replace(".json", "")
            if not os.path.exists(os.path.join(courses_dir, slug)):
                new_courses.append(os.path.join(courses_dir, file))

    if new_courses:
        print(f"✨ Found {len(new_courses)} new courses to review and process.")
        for course_json in new_courses:
            # 2. Run Cross-Model Review
            if run_script("review_course.py", course_json):
                # 3. Generate Social Media & YouTube assets
                run_script("generate_social.py", course_json)
    else:
        print("ℹ️ No new courses need processing.")

    # 4. Compile the static site and deploy to Cloudflare Pages
    # It compiles all JSON to HTML and pushes changes via Git
    run_script("deploy.py")
    
    print("🌅 Daily pipeline run completed.")

if __name__ == "__main__":
    main()
