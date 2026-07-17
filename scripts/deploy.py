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
<title>{title} | AI Rank One</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/svg+xml" href="../../assets/images/icon.svg">
<link rel="manifest" href="../../manifest.json">
<meta name="theme-color" content="#0f172a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>*{{font-family:'IBM Plex Sans Arabic',sans-serif}}code,pre{{font-family:'JetBrains Mono',monospace;direction:ltr;text-align:left}}.prose{{max-width:none;color:#e2e8f0;line-height:1.8}}.prose h1,.prose h2,.prose h3{{font-weight:700;color:#fff;margin:1.5rem 0 1rem}}.prose h1{{font-size:1.8em}}.prose h2{{font-size:1.4em;border-bottom:1px solid rgba(255,255,255,.05);padding-bottom:.5rem}}.prose p{{margin-bottom:1.25rem}}.prose ul{{list-style:disc;padding-inline-start:1.5rem;margin-bottom:1.25rem}}.prose code{{background:rgba(255,255,255,.05);padding:.2rem .4rem;border-radius:.25rem;color:#59b0ff}}.prose pre{{background:#0f172a;padding:1.25rem;border-radius:.75rem;overflow-x:auto;margin:1.5rem 0}}</style>
</head>
<body class="bg-slate-950 text-white" x-data="courseView">
<nav class="fixed top-0 inset-x-0 z-50 bg-slate-950/80 backdrop-blur border-b border-white/5">
  <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
    <a href="../../index.html" class="text-lg font-bold text-blue-400">AI Rank One</a>
    <div class="flex items-center gap-4 text-sm">
      <a href="../../index.html" class="text-slate-200 hover:text-white">الرئيسية</a>
      <a href="../../index.html#news" class="text-slate-200 hover:text-white">النشرة</a>
      <span x-show="user" x-text="user?.email" class="text-slate-300"></span>
      <button x-show="user" @click="signOut()" class="text-red-400">خروج</button>
    </div>
  </div>
</nav>
<main class="pt-24 pb-20 max-w-4xl mx-auto px-4">
  <h1 class="text-3xl font-extrabold mb-4" x-text="course.title"></h1>
  <p class="text-slate-300 text-lg mb-8" x-text="course.description"></p>
  <div class="flex border-b border-white/10 mb-8 overflow-x-auto whitespace-nowrap">
    <template x-for="(mod,index) in course.modules" :key="index">
      <button @click="activeModule=index" class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors" :class="activeModule===index?'border-blue-500 text-blue-400':'border-transparent text-slate-300 hover:text-white'" x-text="'الوحدة '+(index+1)"></button>
    </template>
  </div>
  <div class="prose">
    <h2 class="text-xl font-bold mb-4" x-show="course.modules && course.modules[activeModule]" x-text="course.modules[activeModule]?.title"></h2>
    <div x-show="loading" class="flex justify-center my-12"><svg class="w-8 h-8 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg></div>
    <div x-show="!loading && (activeModule===0 || hasAccess) && course.modules && course.modules[activeModule]">
      <div x-html="renderMarkdown(course.modules[activeModule]?.content)"></div>
      <div x-show="course.modules[activeModule]?.resources?.length" class="not-prose mt-10 pt-6 border-t border-white/10">
        <h3 class="text-lg font-bold text-white mb-4">مصادر إضافية موصى بها</h3>
        <div class="grid gap-3 sm:grid-cols-2">
          <template x-for="(res,ri) in (course.modules[activeModule]?.resources||[])" :key="ri">
            <a :href="res.url" target="_blank" rel="noopener" class="flex items-start gap-3 p-4 rounded-xl bg-white/5 border border-white/10 hover:border-blue-500/40 hover:bg-white/10 transition-colors">
              <span class="text-lg shrink-0" x-text="({article:'📄',paper:'🎓',video:'🎬',podcast:'🎧',docs:'📘'})[res.type]||'🔗'"></span>
              <span class="min-w-0">
                <span class="block text-sm font-semibold text-blue-300 truncate" x-text="res.title"></span>
                <span x-show="res.source" class="block text-xs text-slate-400 mt-0.5" x-text="res.source"></span>
              </span>
            </a>
          </template>
        </div>
      </div>
    </div>
    <div x-show="!loading && activeModule>0 && !hasAccess && course.slug" class="p-8 rounded-2xl bg-blue-950/20 border border-blue-500/20 text-center my-8">
      <h3 class="text-xl font-bold mb-2">هذه الوحدة مغلقة</h3>
      <p class="text-slate-300 text-sm max-w-md mx-auto mb-6">الوحدات من 2 إلى 5 حصرية للمشتركين. اشترك لفتح كامل المحتوى والكود والشهادة!</p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
        <a href="../../index.html#pricing" class="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-sm font-semibold text-center">اشترك في الدورة</a>
        <a href="../../index.html#news" class="px-6 py-3 rounded-xl border border-white/10 hover:bg-white/5 text-sm font-semibold text-center">اشترك بالنشرة المجانية</a>
      </div>
    </div>
  </div>
</main>
<div x-show="showAuth" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4" @click.self="showAuth=false">
  <div class="w-full max-w-sm bg-slate-900 rounded-2xl border border-white/10 p-6">
    <template x-if="!otpSent">
      <form @submit.prevent="sendOTP()">
        <input type="email" x-model="authEmail" required placeholder="بريدك الإلكتروني" dir="ltr" class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/10 text-white text-sm mb-3">
        <button class="w-full py-3 rounded-xl bg-blue-600 font-semibold" :disabled="loading">إرسال رمز التحقق</button>
      </form>
    </template>
    <template x-if="otpSent">
      <form @submit.prevent="verifyOTP()">
        <input type="text" x-model="authOTP" required placeholder="رمز (6 أرقام)" maxlength="6" dir="ltr" class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-white/10 text-white text-sm mb-3 text-center tracking-[0.3em]">
        <button class="w-full py-3 rounded-xl bg-blue-600 font-semibold">تأكيد الدخول</button>
      </form>
    </template>
    <p x-show="authError" x-text="authError" class="mt-3 text-xs text-red-400 text-center"></p>
  </div>
</div>
<script id="course-data" type="application/json">
{course_json}
</script>
<script src="../../assets/js/config.js"></script>
<script>
const SUPABASE_URL = window.PUBLIC_CONFIG?.SUPABASE_URL;
const SUPABASE_ANON_KEY = window.PUBLIC_CONFIG?.SUPABASE_ANON_KEY;
const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
window.courseView = function(){return{{
  course:{{}}, activeModule:0, hasAccess:false, user:null, loading:false,
  showAuth:false, otpSent:false, authEmail:'', authOTP:'', authError:'', loading:false,
  init(){{
    this.course = JSON.parse(document.getElementById('course-data').textContent);
    this.$watch('activeModule', () => this.loadModule());
    sb.auth.getSession().then(({{data}}) => {{ this.user = data.session?.user||null; this.checkAccess(); }});
    sb.auth.onAuthStateChange((e,s) => {{ this.user=s?.user||null; if(e==='SIGNED_IN') this.showAuth=false; this.checkAccess(); }});
  }},
  async checkAccess(){{
    if(!this.user){{ this.hasAccess=false; this.loadModule(); return; }}
    const {{data}} = await sb.from('user_course_access').select('*').eq('course_slug',this.course.slug).maybeSingle();
    this.hasAccess = !!data; this.loadModule();
  }},
  async loadModule(){{
    const i=this.activeModule; if(i===0) return;
    if(this.hasAccess && this.course.modules[i] && !this.course.modules[i].content){{
      this.loading=true;
      const {{data,error}} = await sb.from('course_modules').select('content').eq('course_slug',this.course.slug).eq('module_index',i).single();
      if(!error && data) this.course.modules[i].content=data.content;
      this.loading=false;
    }}
  }},
  async sendOTP(){{ this.loading=true; this.authError=''; try{{ const {{error}}=await sb.auth.signInWithOtp({{email:this.authEmail}}); if(error) throw error; this.otpSent=true; }}catch(e){{ this.authError=e.message||'خطأ'; }} this.loading=false; }},
  async verifyOTP(){{ this.loading=true; this.authError=''; try{{ const {{error}}=await sb.auth.verifyOtp({{email:this.authEmail,token:this.authOTP,type:'email'}}); if(error) throw error; this.showAuth=false; }}catch(e){{ this.authError=e.message||'رمز خاطئ'; }} this.loading=false; }},
  async signOut(){{ await sb.auth.signOut(); this.user=null; this.hasAccess=false; }},
  renderMarkdown(md){{ return md ? marked.parse(md) : ''; }}
}};}};
</script>
</body>
</html>
"""

def generate_config():
    """Generate site/assets/js/config.js from .env so keys live in ONE place."""
    supabase_url = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "YOUR_ANON_KEY")
    variant_id = os.getenv("LEMON_SQUEEZY_VARIANT_ID", "VARIANT_ID")
    bundle_variant_id = os.getenv("LEMON_SQUEEZY_BUNDLE_VARIANT_ID", "bundle-variant-id")
    all_access_variant_id = os.getenv("LEMON_SQUEEZY_ALL_ACCESS_VARIANT_ID", "all-access-variant-id")
    # Flip to "true" in .env once the Lemon Squeezy store is approved + live.
    store_ready = os.getenv("LEMON_STORE_READY", "false")

    config_content = (
        "// AUTO-GENERATED by scripts/deploy.py from .env — do not edit manually.\n"
        "// The Supabase anon key is public by design (protected by Row-Level Security).\n"
        "window.PUBLIC_CONFIG = {\n"
        f'  SUPABASE_URL: "{supabase_url}",\n'
        f'  SUPABASE_ANON_KEY: "{anon_key}",\n'
        f'  LEMON_VARIANT_ID: "{variant_id}",\n'
        f'  LEMON_BUNDLE_VARIANT_ID: "{bundle_variant_id}",\n'
        f'  LEMON_ALL_ACCESS_VARIANT_ID: "{all_access_variant_id}",\n'
        f'  LEMON_STORE_READY: "{store_ready}",\n'
        f'  SUBSCRIBER_COUNT_FN: "{supabase_url.rstrip("/")}/functions/v1/subscriber-count",\n'
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

    We replace the courses array inside the Alpine `app()` data with a real JS
    array literal. This guarantees the course grid renders immediately.
    """
    index_path = os.path.join("site", "index.html")
    if not os.path.exists(index_path):
        return

    import re
    courses_js = json.dumps(courses_list, ensure_ascii=False)

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Greedy match of the FULL courses array (from `courses: [` to the last `],`
    # that precedes the `// Init` comment). The previous non-greedy `.*?\],`
    # matched only up to the first course's closing bracket, corrupting the array.
    pattern = r"courses:\s*\[.*\],\s*\n"
    replacement = f"courses: {courses_js},\n"

    new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if count == 0:
        print("⚠️  courses list pattern not found in index.html — skipping inject")
        return

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
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

    url_courses = f"{supabase_url.rstrip('/')}/rest/v1/courses?on_conflict=slug"
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
    url_modules = f"{supabase_url.rstrip('/')}/rest/v1/course_modules?on_conflict=course_slug,module_index"
    for idx, mod in enumerate(course_data.get("modules", [])):
        module_payload = {
            "course_slug": slug,
            "module_index": idx,
            "title": mod.get("title", ""),
            "content": mod.get("content", ""),
            "resources": mod.get("resources", [])
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
                mod["resources"] = []  # Curated resources are paid value too.

        html_content = (
            COURSE_TEMPLATE
            .replace("{title}", course_data.get("title", ""))
            .replace("{description}", course_data.get("description", ""))
            .replace("{course_json}", json.dumps(public_course_data, ensure_ascii=False))
            # Convert doubled braces (used to escape JS in the template) to single.
            .replace("{{", "{").replace("}}", "}")
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
