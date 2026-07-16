import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Ensure emoji/Arabic prints work on Windows consoles (cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

COURSE_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | منصة الذكاء الاصطناعي العربية</title>
    <meta name="description" content="{description}">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0f172a">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        arabic: ['"IBM Plex Sans Arabic"', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }},
                    colors: {{
                        brand: {{ 400: '#59b0ff', 500: '#338dff', 600: '#1b6ff5', 950: '#142957' }},
                        surface: {{ 50: '#f8fafc', 200: '#e2e8f0', 700: '#334155', 800: '#1e293b', 900: '#0f172a', 950: '#020617' }}
                    }}
                }}
            }}
        }}
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        * {{ font-family: 'IBM Plex Sans Arabic', sans-serif; }}
        .prose code {{ font-family: 'JetBrains Mono', monospace; direction: ltr; text-align: left; background-color: rgba(255,255,255,0.05); padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.875em; color: #59b0ff; }}
        .prose pre {{ background: #0f172a; padding: 1.25rem; border-radius: 0.75rem; overflow-x: auto; border: 1px border-white/5; margin: 1.5rem 0; }}
        .prose pre code {{ background: transparent; padding: 0; border-radius: 0; color: #fff; font-size: 0.9em; }}
        .prose h1, .prose h2, .prose h3 {{ font-weight: 700; color: #fff; margin-top: 2rem; margin-bottom: 1rem; }}
        .prose h1 {{ font-size: 1.8em; }}
        .prose h2 {{ font-size: 1.4em; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; }}
        .prose p {{ color: #e2e8f0; line-height: 1.8; margin-bottom: 1.25rem; }}
        .prose ul {{ list-style-type: disc; padding-inline-start: 1.5rem; margin-bottom: 1.25rem; color: #e2e8f0; }}
        .prose li {{ margin-bottom: 0.5rem; }}
    </style>
</head>
<body class="bg-surface-950 text-white font-arabic antialiased" x-data="courseView()">

    <!-- Navbar -->
    <nav class="fixed top-0 inset-x-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-white/5">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
            <a href="/" class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                </div>
                <span class="text-lg font-bold bg-gradient-to-l from-brand-400 to-purple-400 bg-clip-text text-transparent">AI Rank One</span>
            </a>
            <div class="flex items-center gap-6">
                <a href="/" class="text-sm text-surface-200 hover:text-white transition-colors">الرئيسية</a>
                <span x-show="user" class="text-sm text-surface-200" x-text="user.email"></span>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="pt-24 pb-20 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-extrabold mb-4" x-text="course.title"></h1>
        <p class="text-surface-200 text-lg mb-8 leading-relaxed" x-text="course.description"></p>

        <!-- Module Navigation Tabs -->
        <div class="flex border-b border-white/10 mb-8 overflow-x-auto whitespace-nowrap">
            <template x-for="(mod, index) in course.modules" :key="index">
                <button
                    @click="activeModule = index"
                    class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors"
                    :class="activeModule === index ? 'border-brand-500 text-brand-400' : 'border-transparent text-surface-200 hover:text-white'"
                    x-text="'الوحدة ' + (index + 1)"
                ></button>
            </template>
        </div>

        <!-- Render Content -->
        <div class="prose prose-invert max-w-none">
            <!-- Module Header -->
            <h2 class="text-xl font-bold mb-4" x-text="course.modules[activeModule]?.title"></h2>

            <!-- Module Body -->
            <div x-show="activeModule === 0 || hasAccess">
                <div x-html="renderMarkdown(course.modules[activeModule]?.content)"></div>
            </div>

            <!-- Paywall Overlay for Modules 2-5 -->
            <div x-show="activeModule > 0 && !hasAccess" class="p-8 rounded-2xl bg-gradient-to-br from-brand-950/20 to-purple-950/20 border border-brand-500/20 text-center my-8">
                <svg class="w-12 h-12 text-brand-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                <h3 class="text-xl font-bold mb-2">هذه الوحدة مغلقة</h3>
                <p class="text-surface-200 text-sm max-w-md mx-auto mb-6">اشترك الآن لفتح جميع الوحدات التقنية الأربعة الإضافية والحصول على الكود المصدري وشهادة الإتمام.</p>
                <a :href="'https://checkout.lemonsqueezy.com/checkout/buy/' + (window.PUBLIC_CONFIG?.LEMON_VARIANT_ID || 'VARIANT_ID') + '?checkout[custom][course_slug]=' + course.slug" id="checkout-btn" class="inline-block px-8 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 font-semibold text-white transition-all shadow-lg shadow-brand-600/25">
                    اشترك الآن مقابل {price}$ فقط
                </a>
            </div>
        </div>
    </main>

    <!-- Script Data Injected by Compiler -->
    <script id="course-data" type="application/json">
    {course_json}
    </script>

    <script src="/assets/js/config.js"></script>
    <script src="/assets/js/paywall.js"></script>
    <script>
        // Supabase Init (config loaded from /assets/js/config.js, generated from .env)
        const SUPABASE_URL = window.PUBLIC_CONFIG?.SUPABASE_URL;
        const SUPABASE_ANON_KEY = window.PUBLIC_CONFIG?.SUPABASE_ANON_KEY;
        let supabase;
        try {{ supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY); }} catch(e) {{}}

        function courseView() {{
            return {{
                course: {{}},
                activeModule: 0,
                hasAccess: false,
                user: null,

                async init() {{
                    this.course = JSON.parse(document.getElementById('course-data').textContent);
                    if (!supabase) return;
                    
                    const {{ data: {{ session }} }} = await supabase.auth.getSession();
                    if (session) {{
                        this.user = session.user;
                        const {{ data, error }} = await supabase
                            .from('user_course_access')
                            .select('*')
                            .eq('course_slug', this.course.slug)
                            .maybeSingle();
                        if (data && !error) {{
                            this.hasAccess = true;
                        }}
                    }}
                }},

                renderMarkdown(md) {{
                    return md ? marked.parse(md) : '';
                }}
            }}
        }}
    </script>
</body>
</html>
"""

def generate_config():
    """Generate site/assets/js/config.js from .env so keys live in ONE place."""
    supabase_url = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "YOUR_ANON_KEY")
    variant_id = os.getenv("LEMON_SQUEEZY_VARIANT_ID", "VARIANT_ID")

    config_content = (
        "// AUTO-GENERATED by scripts/deploy.py from .env — do not edit manually.\n"
        "// The Supabase anon key is public by design (protected by Row-Level Security).\n"
        "window.PUBLIC_CONFIG = {\n"
        f'  SUPABASE_URL: "{supabase_url}",\n'
        f'  SUPABASE_ANON_KEY: "{anon_key}",\n'
        f'  LEMON_VARIANT_ID: "{variant_id}",\n'
        "};\n"
    )

    config_path = os.path.join("site", "assets", "js", "config.js")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    if anon_key == "YOUR_ANON_KEY":
        print("⚠️  config.js written with PLACEHOLDERS — set SUPABASE_ANON_KEY etc. in .env")
    else:
        print("🔑 Generated: site/assets/js/config.js (from .env)")


def compile_and_deploy():
    print("🚀 Compiling courses and preparing deployment...")
    generate_config()
    courses_list = []
    
    # Read course JSON files
    courses_dir = "site/courses"
    if not os.path.exists(courses_dir):
        print("No courses directory found.")
        return
        
    for file in os.listdir(courses_dir):
        if not file.endswith(".json") or file == "_index.json":
            continue
            
        filepath = os.path.join(courses_dir, file)
        with open(filepath, "r", encoding="utf-8") as f:
            course_data = json.load(f)
            
        slug = file.replace(".json", "")
        course_data["slug"] = slug
        
        # Add to index list for the home page listing
        courses_list.append({
            "slug": slug,
            "title": course_data.get("title", ""),
            "description": course_data.get("description", ""),
            "tags": course_data.get("tags", []),
            "modules": len(course_data.get("modules", [])),
            "duration": course_data.get("duration", "4 hours"),
            "price": course_data.get("price", 29),
            "gradient": course_data.get("gradient", "from-brand-500 to-blue-500")
        })
        
        # Generate the static course page folder and index.html
        course_page_dir = os.path.join(courses_dir, slug)
        os.makedirs(course_page_dir, exist_ok=True)
        
        html_content = COURSE_TEMPLATE.format(
            title=course_data.get("title", ""),
            description=course_data.get("description", ""),
            course_json=json.dumps(course_data, ensure_ascii=False),
            price=course_data.get("price", 29)
        )
        
        with open(os.path.join(course_page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"📄 Compiled: {course_page_dir}/index.html")
        
    # Write global courses list
    with open(os.path.join(courses_dir, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(courses_list, f, ensure_ascii=False, indent=2)
    print("📄 Updated: site/courses/_index.json")

    # Update index.html to load courses dynamically via Alpine
    # Wait, our index.html already loads courses from "courses" array. We should inject the dynamic list!
    # Let's read site/index.html and replace the course list payload.
    # To keep it extremely simple, we can have Alpine fetch "/courses/_index.json" on init!
    # Yes! Let's edit index.html's init() to fetch courses dynamically.

    # Git Deploy
    print("📤 Pushing to Cloudflare Pages (via git)...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-compiled courses and assets"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🎉 Deployment completed successfully!")
    except Exception as e:
        print(f"⚠️ Git push failed (may not have set up remote or no changes): {e}")

if __name__ == "__main__":
    compile_and_deploy()
