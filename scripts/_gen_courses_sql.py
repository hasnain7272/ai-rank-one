import json, glob, os

rows = []
for f in glob.glob("site/courses/*.json"):
    slug = os.path.basename(f).replace(".json", "")
    if slug == "_index":
        continue
    d = json.load(open(f, encoding="utf-8"))
    esc = lambda s: (s or "").replace("'", "''")
    tags = "{" + ",".join(f'"{esc(t)}"' for t in d.get("tags", [])) + "}"
    rows.append(
        f"INSERT INTO public.courses (slug, title, description, tags, modules, duration, price, gradient) "
        f"VALUES ('{slug}', '{esc(d.get('title',''))}', '{esc(d.get('description',''))}', '{tags}', "
        f"{len(d.get('modules', []))}, '{esc(d.get('duration',''))}', {d.get('price',29)}, '{esc(d.get('gradient',''))}') "
        f"ON CONFLICT (slug) DO UPDATE SET title=EXCLUDED.title, description=EXCLUDED.description, "
        f"tags=EXCLUDED.tags, modules=EXCLUDED.modules, duration=EXCLUDED.duration, price=EXCLUDED.price, gradient=EXCLUDED.gradient;"
    )

open("temp_courses.sql", "w", encoding="utf-8").write("\n".join(rows))
print(f"Generated {len(rows)} course metadata rows")
