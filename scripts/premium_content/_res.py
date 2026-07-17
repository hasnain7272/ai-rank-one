# -*- coding: utf-8 -*-
def res(items):
    icons = {
        "paper": "ورقة بحثية",
        "blog": "مقال / مدونة",
        "video": "فيديو",
        "podcast": "بودكاست",
        "docs": "توثيق رسمي",
    }
    lines = ["", "## مصادر إضافية (للتعمّق — اختَر 1–2 أسبوعياً)", ""]
    for kind, title, url in items:
        lines.append(f"- **{icons.get(kind, kind)}** — [{title}]({url})")
    lines += [
        "",
        "> نصيحة: طبّق كود الوحدة أولاً، ثم عد للمصدر لتربط النظرية بالتنفيذ.",
        "",
    ]
    return "\n".join(lines)
