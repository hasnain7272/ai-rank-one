# -*- coding: utf-8 -*-
"""Compile course pages, sync to Supabase, and push to Cloudflare Pages.

Heavy lifting lives in scripts/_deploy_helpers.py and scripts/course_template.html
to keep this driver small. Run: python scripts/deploy.py
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
import _deploy_helpers as H

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Arabic prints on Windows.
except Exception:
    pass

load_dotenv()
COURSES_DIR = "site/courses"


def compile_and_deploy():
    print("Compiling courses and preparing deployment...")
    H.generate_config()
    if not os.path.isdir(COURSES_DIR):
        print("No courses directory found.")
        return

    cards = []
    for file in sorted(os.listdir(COURSES_DIR)):
        if not file.endswith(".json") or file == "_index.json":
            continue
        slug = file[:-5]
        with open(os.path.join(COURSES_DIR, file), encoding="utf-8") as f:
            data = json.load(f)
        data["slug"] = slug

        cards.append(H.summarize(slug, data))
        H.sync_course_to_supabase(data, slug)

        page_dir = os.path.join(COURSES_DIR, slug)
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(H.compile_course_html(slug, data))
        print("PAGE compiled " + page_dir + "/index.html")

    with open(os.path.join(COURSES_DIR, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print("PAGE updated _index.json")
    H.inject_courses_into_index(cards)
    git_push()


def git_push():
    print("Pushing to Cloudflare Pages (via git)...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-compiled courses and assets"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Deployment completed successfully.")
    except Exception as e:
        print("WARN git push failed (no remote/changes?): %s" % e)


if __name__ == "__main__":
    compile_and_deploy()
