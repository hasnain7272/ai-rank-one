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
    <link rel="manifest" href="../../manifest.json">
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
            <a href="../../index.html" class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                </div>
                <span class="text-lg font-bold bg-gradient-to-l from-brand-400 to-purple-400 bg-clip-text text-transparent">AI Rank One</span>
            </a>
            <div class="flex items-center gap-6">
                <a href="../../index.html" class="text-sm text-surface-200 hover:text-white transition-colors">الرئيسية</a>
                <span x-show="user" class="text-sm text-surface-200" x-text="user.email"></span>
                <button x-show="user" @click="signOut()" class="text-sm text-red-400 hover:text-red-300 transition-colors">تسجيل الخروج</button>
                <button x-show="!user" @click="showAuth = true" class="text-sm text-brand-400 hover:text-brand-300 transition-colors">تسجيل الدخول</button>
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
            <h2 class="text-xl font-bold mb-4" x-show="course.modules && course.modules[activeModule]" x-text="course.modules[activeModule]?.title"></h2>
            <h2 class="text-xl font-bold mb-4" x-show="!course.modules || !course.modules[activeModule]">جارٍ التحميل...</h2>

            <!-- Loading Spinner -->
            <div x-show="loading" class="flex justify-center my-12">
                <svg class="w-8 h-8 animate-spin text-brand-500" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
            </div>

            <!-- Module Body -->
            <div x-show="!loading && (activeModule === 0 || hasAccess) && course.modules && course.modules[activeModule]">
                <div x-html="renderMarkdown(course.modules[activeModule]?.content)"></div>
            </div>

            <!-- Paywall Overlay for Modules 2-5 -->
            <div x-show="!loading && activeModule > 0 && !hasAccess && course.slug" class="p-8 rounded-2xl bg-gradient-to-br from-brand-950/20 to-purple-950/20 border border-brand-500/20 text-center my-8">
                <svg class="w-12 h-12 text-brand-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                <h3 class="text-xl font-bold mb-2">هذه الوحدة مغلقة</h3>
                <p class="text-surface-200 text-sm max-w-md mx-auto mb-6">الوحدات من 2 إلى 5 حصرية للمشتركين. يرجى الاشتراك في الدورة لفتح كامل المحتوى وكود المصدر والشهادة فوراً!</p>
                
                <div class="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                    <a href="../../index.html#pricing" class="w-full sm:w-auto px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-sm font-semibold text-white transition-all text-center">
                        اشترك في الدورة
                    </a>
                    <button @click="showAuth = true" class="w-full sm:w-auto px-6 py-3 rounded-xl border border-white/10 hover:bg-white/5 text-sm font-semibold text-surface-200 hover:text-white transition-all">
                        تسجيل الدخول للمشتركين
                    </button>
                </div>
            </div>
        </div>
    </main>

    <!-- AUTH MODAL -->
    <div x-show="showAuth" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100" x-transition:leave="transition ease-in duration-150" x-transition:leave-start="opacity-100" x-transition:leave-end="opacity-0" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" @click.self="showAuth = false" style="display: none;">
        <div class="w-full max-w-sm bg-surface-900 rounded-2xl border border-white/10 p-6 shadow-2xl" @click.stop>
            <div class="text-center mb-6">
                <h3 class="text-xl font-bold mb-1">تسجيل الدخول</h3>
                <p class="text-sm text-surface-200">سنرسل لك رمز تحقق على بريدك الإلكتروني</p>
            </div>

            <!-- Step 1: Email -->
            <form x-show="authStep === 'email'" @submit.prevent="sendOTP()">
                <input
                    type="email"
                    x-model="authEmail"
                    required
                    placeholder="بريدك الإلكتروني"
                    class="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/10 text-white placeholder:text-surface-700 focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/50 text-sm mb-3"
                    dir="ltr"
                >
                <button type="submit" class="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-sm font-semibold text-white transition-all" :disabled="authLoading">
                    <span x-show="!authLoading">إرسال رمز التحقق</span>
                    <span x-show="authLoading" class="flex items-center justify-center gap-2">
                        <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                        جاري الإرسال...
                    </span>
                </button>
            </form>

            <!-- Step 2: OTP -->
            <form x-show="authStep === 'otp'" @submit.prevent="verifyOTP()">
                <p class="text-xs text-surface-200 mb-3 text-center">أدخل الرمز المرسل إلى <span class="text-white" x-text="authEmail" dir="ltr"></span></p>
                <input
                    type="text"
                    x-model="authOTP"
                    required
                    placeholder="رمز التحقق (6 أرقام)"
                    maxlength="6"
                    class="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/10 text-white placeholder:text-surface-700 focus:outline-none focus:border-brand-500/50 text-sm mb-3 text-center tracking-[0.3em]"
                    dir="ltr"
                >
                <button type="submit" class="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-sm font-semibold text-white transition-all" :disabled="authLoading">
                    تأكيد الدخول
                </button>
                <button type="button" @click="authStep = 'email'" class="w-full mt-2 py-2 text-xs text-surface-200 hover:text-white transition-colors">
                    إرسال رمز جديد
                </button>
            </form>

            <!-- Error -->
            <p x-show="authError" x-text="authError" class="mt-3 text-xs text-red-400 text-center"></p>
        </div>
    </div>

    <!-- Script Data Injected by Compiler -->
    <script id="course-data" type="application/json">
    {course_json}
    </script>

    <script src="../../assets/js/config.js"></script>
    <script>
        // Supabase Init loaded from config.js
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
                loading: false,
                message: '',
                
                // Auth modal state
                showAuth: false,
                authStep: 'email',
                authEmail: '',
                authOTP: '',
                authLoading: false,
                authError: '',

                async init() {{
                    this.course = JSON.parse(document.getElementById('course-data').textContent);
                    
                    // Watch for activeModule changes to fetch gated content
                    this.$watch('activeModule', async (value) => {{
                        await this.loadActiveModule();
                    }});

                    if (!supabase) {{
                        // Offline/demo fallback
                        this.hasAccess = true;
                        return;
                    }}
                    
                    const {{ data: {{ session }} }} = await supabase.auth.getSession();
                    this.user = session?.user || null;
                    await this.checkAccess();

                    // Listen for auth changes
                    supabase.auth.onAuthStateChange(async (event, session) => {{
                        this.user = session?.user || null;
                        if (event === 'SIGNED_IN') {{
                            this.showAuth = false;
                        }}
                        await this.checkAccess();
                    }});
                }},

                async checkAccess() {{
                    if (!supabase) return;
                    if (!this.user) {{
                        this.hasAccess = false;
                        return;
                    }}
                    
                    try {{
                        const {{ data, error }} = await supabase
                            .from('user_course_access')
                            .select('*')
                            .eq('course_slug', this.course.slug)
                            .maybeSingle();
                        
                        if (error) throw error;
                        this.hasAccess = !!data;
                    }} catch (e) {{
                        console.error('Error checking course access:', e);
                        this.hasAccess = false;
                    }}
                    
                    await this.loadActiveModule();
                }},

                async loadActiveModule() {{
                    const idx = this.activeModule;
                    if (idx === 0) return; // Module 1 is always embedded statically
                    
                    if (this.hasAccess && this.course.modules && this.course.modules[idx] && !this.course.modules[idx].content) {{
                        this.loading = true;
                        this.message = '';
                        try {{
                            const {{ data, error }} = await supabase
                                .from('course_modules')
                                .select('content')
                                .eq('course_slug', this.course.slug)
                                .eq('module_index', idx)
                                .single();
                            
                            if (error) throw error;
                            if (data) {{
                                this.course.modules[idx].content = data.content;
                            }}
                        }} catch (e) {{
                            console.error('Error loading module content:', e);
                            this.message = 'حدث خطأ أثناء تحميل محتوى الوحدة: ' + (e.message || e);
                        }}
                        this.loading = false;
                    }}
                }},

                // Auth methods
                async sendOTP() {{
                    if (!supabase) {{ this.authError = 'Auth not configured'; return; }}
                    this.authLoading = true;
                    this.authError = '';
                    try {{
                        const {{ error }} = await supabase.auth.signInWithOtp({{
                            email: this.authEmail,
                        }});
                        if (error) throw error;
                        this.authStep = 'otp';
                    }} catch (e) {{
                        this.authError = e.message || 'حدث خطأ — حاول مرة أخرى';
                    }}
                    this.authLoading = false;
                }},

                async verifyOTP() {{
                    if (!supabase) return;
                    this.authLoading = true;
                    this.authError = '';
                    try {{
                        const {{ error }} = await supabase.auth.verifyOtp({{
                            email: this.authEmail,
                            token: this.authOTP,
                            type: 'email',
                        }});
                        if (error) throw error;
                        this.showAuth = false;
                    }} catch (e) {{
                        this.authError = e.message || 'رمز غير صحيح — حاول مرة أخرى';
                    }}
                    this.authLoading = false;
                }},

                async signOut() {{
                    if (!supabase) return;
                    await supabase.auth.signOut();
                    this.user = null;
                    this.hasAccess = false;
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


def inject_courses_into_index(courses_list):
    """Inject the compiled course list directly into site/index.html.

    We replace the placeholder token `/*COURSES_PLACEHOLDER*/` inside the
    Alpine `app()` data with a real JS array literal. This guarantees the
    course grid renders immediately, with no async fetch / undefined flash.
    """
    index_path = os.path.join("site", "index.html")
    if not os.path.exists(index_path):
        return

    courses_js = json.dumps(courses_list, ensure_ascii=False)
    token = "/*COURSES_PLACEHOLDER*/"
    placeholder = f"courses: {token},"
    replacement = f"courses: {courses_js},"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if token not in html:
        print("⚠️  courses placeholder token not found in index.html — skipping inject")
        return

    html = html.replace(placeholder, replacement, 1)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("📄 Injected course list into site/index.html")


def sync_course_to_supabase(course_data, slug):
    """Sync course details and modules to Supabase tables."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key or "your_" in supabase_url or "YOUR_" in supabase_url:
        print("⚠️ Supabase credentials not configured in env, skipping database sync.")
        return

    import requests
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # 1. Sync courses metadata
    course_payload = {
        "slug": slug,
        "title": course_data.get("title", ""),
        "description": course_data.get("description", ""),
        "tags": course_data.get("tags", []),
        "modules": len(course_data.get("modules", [])),
        "duration": course_data.get("duration", "4 hours"),
        "price": course_data.get("price", 29),
        "gradient": course_data.get("gradient", "from-brand-500 to-blue-500")
    }

    url_courses = f"{supabase_url.rstrip('/')}/rest/v1/courses"
    try:
        r = requests.post(url_courses, json=course_payload, headers=headers)
        if r.status_code not in [200, 201]:
            print(f"❌ Supabase course sync failed for {slug}: {r.status_code} - {r.text}")
            return
        print(f"✅ Synced course metadata: {slug}")
    except Exception as e:
        print(f"❌ Supabase connection error during course sync: {e}")
        return

    # 2. Sync module contents to course_modules
    url_modules = f"{supabase_url.rstrip('/')}/rest/v1/course_modules"
    for idx, mod in enumerate(course_data.get("modules", [])):
        module_payload = {
            "course_slug": slug,
            "module_index": idx,
            "title": mod.get("title", ""),
            "content": mod.get("content", "")
        }
        try:
            r = requests.post(url_modules, json=module_payload, headers=headers)
            if r.status_code not in [200, 201]:
                print(f"❌ Supabase module sync failed for {slug} (module {idx+1}): {r.status_code} - {r.text}")
            else:
                print(f"✅ Synced course module {idx+1} for {slug}")
        except Exception as e:
            print(f"❌ Supabase connection error during module sync: {e}")


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
        
        # Sync the complete course details and modules to Supabase database
        sync_course_to_supabase(course_data, slug)

        # Create a public version of course JSON data with gated module content stripped
        import copy
        public_course_data = copy.deepcopy(course_data)
        for idx, mod in enumerate(public_course_data.get("modules", [])):
            if idx > 0:
                mod["content"] = ""  # Clear paid content to prevent scraping!

        html_content = COURSE_TEMPLATE.format(
            title=course_data.get("title", ""),
            description=course_data.get("description", ""),
            course_json=json.dumps(public_course_data, ensure_ascii=False),
            price=course_data.get("price", 29)
        )
        
        with open(os.path.join(course_page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"📄 Compiled: {course_page_dir}/index.html")
        
    # Write global courses list
    with open(os.path.join(courses_dir, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(courses_list, f, ensure_ascii=False, indent=2)
    print("📄 Updated: site/courses/_index.json")

    # Inject the course list directly into index.html so courses render without
    # depending on an async fetch (which can briefly show "no courses").
    inject_courses_into_index(courses_list)

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
