-- Initial Schema for Arabic AI Platform (idempotent — safe to re-run)
-- NOTE: tables already exist on the linked remote; guards prevent errors on re-push.

-- 1. Courses Table
CREATE TABLE IF NOT EXISTS public.courses (
    slug TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT[],
    modules INTEGER DEFAULT 5,
    duration TEXT,
    price NUMERIC NOT NULL,
    gradient TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Course Access Table (Gates premium modules)
CREATE TABLE IF NOT EXISTS public.user_course_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_slug TEXT NOT NULL REFERENCES public.courses(slug) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, course_slug)
);

-- Enable RLS for Course Access
ALTER TABLE public.user_course_access ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own access" ON public.user_course_access;
CREATE POLICY "Users can view their own access" ON public.user_course_access
    FOR SELECT USING (auth.uid() = user_id);

-- 3. Certificates Table
CREATE TABLE IF NOT EXISTS public.certificates (
    code TEXT PRIMARY KEY, -- e.g., CERT-XXXXXX
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    date DATE DEFAULT CURRENT_DATE NOT NULL,
    score TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for Certificates (Publicly readable for verification, but only insertable by service role/edge function)
ALTER TABLE public.certificates ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public read access for certificates" ON public.certificates;
CREATE POLICY "Public read access for certificates" ON public.certificates
    FOR SELECT USING (true);

-- 4. Newsletter Subscribers Table
CREATE TABLE IF NOT EXISTS public.subscribers (
    email TEXT PRIMARY KEY,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for Subscribers (Insertable by public/anon, readable only by service_role)
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Anyone can subscribe" ON public.subscribers;
CREATE POLICY "Anyone can subscribe" ON public.subscribers
    FOR INSERT WITH CHECK (true);
