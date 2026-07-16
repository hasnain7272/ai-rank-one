import json, glob, os

courses_dir = "site/courses"
rows = []
for f in glob.glob(os.path.join(courses_dir, "*.json")):
    slug = os.path.basename(f).replace(".json", "")
    if slug == "_index":
        continue
    data = json.load(open(f, encoding="utf-8"))
    for idx, mod in enumerate(data.get("modules", [])):
        content = mod.get("content", "") or ""
        title = mod.get("title", "")
        # Escape single quotes for SQL literal
        esc = lambda s: s.replace("'", "''")
        rows.append(
            f"INSERT INTO public.course_modules (course_slug, module_index, title, content) "
            f"VALUES ('{slug}', {idx}, '{esc(title)}', '{esc(content)}') "
            f"ON CONFLICT (course_slug, module_index) DO UPDATE SET title = EXCLUDED.title, content = EXCLUDED.content;"
        )

sql = "\n".join(rows)
open("temp_modules.sql", "w", encoding="utf-8").write(sql)
print(f"Generated {len(rows)} module rows for {len([r for r in glob.glob(os.path.join(courses_dir,'*.json')) if '_index' not in r])} courses")
