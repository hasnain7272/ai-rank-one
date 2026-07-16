// Paywall Gating Logic
document.addEventListener('DOMContentLoaded', async () => {
    const premiumContent = document.getElementById('premium-content');
    const paywallOverlay = document.getElementById('paywall-overlay');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (!premiumContent || !paywallOverlay) return;

    // Get current course slug from URL path (e.g., /courses/langgraph/ -> langgraph)
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const courseSlug = pathParts[pathParts.length - 1] || 'langgraph';

    // Check if Supabase client is initialized on the window
    if (!window.supabase) {
        console.warn('Supabase not configured. Running in developer preview mode.');
        return;
    }

    const { data: { session } } = await window.supabase.auth.getSession();

    if (session) {
        const user = session.user;
        
        // Query user course access
        const { data, error } = await window.supabase
            .from('user_course_access')
            .select('*')
            .eq('course_slug', courseSlug)
            .maybeSingle();

        if (data && !error) {
            // User has paid, reveal premium content
            premiumContent.classList.remove('hidden');
            paywallOverlay.classList.add('hidden');
            return;
        }

        // Prefill Lemon Squeezy checkout link with user's email
        if (checkoutBtn) {
            const baseUrl = checkoutBtn.getAttribute('href');
            if (baseUrl && !baseUrl.includes('checkout.lemonsqueezy.com')) {
                checkoutBtn.setAttribute('href', `${baseUrl}?checkout[email]=${encodeURIComponent(user.email)}&checkout[custom][course_slug]=${courseSlug}`);
            }
        }
    }
});
