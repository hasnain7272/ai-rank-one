// Shared course-page logic for AI Rank One. Single source of truth — loaded by every course page.
// Supabase init (config.js must load first)
const SUPABASE_URL = window.PUBLIC_CONFIG?.SUPABASE_URL;
const SUPABASE_ANON_KEY = window.PUBLIC_CONFIG?.SUPABASE_ANON_KEY;
let sb = null;
try { sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { auth: { persistSession: false, autoRefreshToken: false } }); } catch (e) {}

function courseView() {
  return {
    course: {},
    activeModule: 0,
    hasAccess: false,
    user: null,
    loading: false,
    message: '',
    showAuth: false,
    authStep: 'email',
    authEmail: '',
    authOTP: '',
    authLoading: false,
    authError: '',

    async init() {
      this.course = JSON.parse(document.getElementById('course-data').textContent);
      this.$watch('activeModule', async () => { await this.loadActiveModule(); });

      if (!sb) { this.hasAccess = true; return; } // offline/demo fallback

      const { data: { session } } = await sb.auth.getSession();
      this.user = session?.user || null;
      await this.checkAccess();

      sb.auth.onAuthStateChange(async (event, session) => {
        this.user = session?.user || null;
        if (event === 'SIGNED_IN') this.showAuth = false;
        await this.checkAccess();
      });
    },

    async checkAccess() {
      if (!sb || !this.user) { this.hasAccess = false; return; }
      try {
        // Unlocked if this course is granted, OR user holds all-access ('*').
        const { data, error } = await sb
          .from('user_course_access')
          .select('course_slug')
          .in('course_slug', [this.course.slug, '*']);
        if (error) throw error;
        this.hasAccess = Array.isArray(data) && data.length > 0;
      } catch (e) {
        console.error('Access check failed:', e);
        this.hasAccess = false;
      }
      await this.loadActiveModule();
    },

    async loadActiveModule() {
      const idx = this.activeModule;
      if (idx === 0) return; // module 1 is embedded statically
      if (this.hasAccess && this.course.modules?.[idx] && !this.course.modules[idx].content) {
        this.loading = true; this.message = '';
        try {
          const { data, error } = await sb
            .from('course_modules').select('content')
            .eq('course_slug', this.course.slug).eq('module_index', idx).single();
          if (error) throw error;
          if (data) this.course.modules[idx].content = data.content;
        } catch (e) {
          console.error('Module load failed:', e);
          this.message = 'حدث خطأ أثناء تحميل محتوى الوحدة: ' + (e.message || e);
        }
        this.loading = false;
      }
    },

    async sendOTP() {
      if (!sb) { this.authError = 'Auth not configured'; return; }
      this.authLoading = true; this.authError = '';
      try {
        const { error } = await sb.auth.signInWithOtp({ email: this.authEmail });
        if (error) throw error;
        this.authStep = 'otp';
      } catch (e) { this.authError = e.message || 'حدث خطأ — حاول مرة أخرى'; }
      this.authLoading = false;
    },

    async verifyOTP() {
      if (!sb) return;
      this.authLoading = true; this.authError = '';
      try {
        const { error } = await sb.auth.verifyOtp({
          email: this.authEmail, token: this.authOTP, type: 'email',
        });
        if (error) throw error;
        this.showAuth = false;
      } catch (e) { this.authError = e.message || 'رمز غير صحيح — حاول مرة أخرى'; }
      this.authLoading = false;
    },

    async signOut() {
      if (!sb) return;
      await sb.auth.signOut();
      this.user = null; this.hasAccess = false;
    },

    renderMarkdown(md) { return md ? marked.parse(md) : ''; },
  };
}
