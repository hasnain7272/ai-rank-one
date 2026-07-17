# -*- coding: utf-8 -*-
"""Builds premium course JSON for all 6 courses. Run: python scripts/premium_content/build_all.py"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parent.parent / "site" / "courses"

import c_langgraph, c_rag, c_lora, c_prompt, c_gov, c_mlops
from _res import MARKER, MARKER_END

_RES_RE = re.compile(re.escape(MARKER) + r"(.*?)" + re.escape(MARKER_END), re.S)


def extract_resources(data):
    """Pull the RES marker out of each module's content into resources[]."""
    for mod in data.get("modules", []):
        content = mod.get("content", "")
        m = _RES_RE.search(content)
        mod["resources"] = json.loads(m.group(1)) if m else []
        mod["content"] = _RES_RE.sub("", content).rstrip() + "\n"
    return data

COURSES = {
    "langgraph-multi-agents": c_langgraph.course,
    "building-a-production-rag-system": c_rag.course,
    "llm-fine-tuning-with-lora-and-qlora": c_lora.course,
    "advanced-prompt-engineering-for-developers": c_prompt.course,
    "ai-governance-and-ethics-in-the-arab-world": c_gov.course,
    "mlops-from-experiment-to-production": c_mlops.course,
}


def save(slug, data):
    data["slug"] = slug
    path = OUT / f"{slug}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {path.name}  ({len(data.get('modules', []))} modules)")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, builder in COURSES.items():
        save(slug, extract_resources(builder()))
    print("Done. Run scripts/deploy.py to compile pages.")
