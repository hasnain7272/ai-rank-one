# -*- coding: utf-8 -*-
import json

ICONS = {
    "paper": "ورقة بحثية",
    "blog": "مقال / مدونة",
    "video": "فيديو",
    "podcast": "بودكاست",
    "docs": "توثيق رسمي",
}

MARKER = "<!--RES:"
MARKER_END = "-->"


def res(items):
    """Return markdown for the resources block PLUS a machine-readable marker.

    build_all.py extracts the marker into a structured `resources[]` array
    (rendered as cards) and strips both the marker and the inline list so the
    JSON stays clean. Inline markdown is kept only as a fallback for any
    consumer that renders raw content.
    """
    lines = ["", "## مصادر إضافية (للتعمّق — اختَر 1–2 أسبوعياً)", ""]
    payload = []
    for kind, title, url in items:
        lines.append(f"- **{ICONS.get(kind, kind)}** — [{title}]({url})")
        payload.append({"type": kind, "title": title, "url": url,
                        "source": ICONS.get(kind, kind)})
    lines += [
        "",
        "> نصيحة: طبّق كود الوحدة أولاً، ثم عد للمصدر لتربط النظرية بالتنفيذ.",
        "",
        MARKER + json.dumps(payload, ensure_ascii=False) + MARKER_END,
    ]
    return "\n".join(lines)
