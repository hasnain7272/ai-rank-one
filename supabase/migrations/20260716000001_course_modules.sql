-- 1. Create course_modules table to store paid modules securely
CREATE TABLE IF NOT EXISTS public.course_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_slug TEXT NOT NULL REFERENCES public.courses(slug) ON DELETE CASCADE,
    module_index INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    UNIQUE(course_slug, module_index)
);

-- Enable RLS for Course Modules
ALTER TABLE public.course_modules ENABLE ROW LEVEL SECURITY;

-- Policy 1: Allow public read access for the first module (index 0) which is free
CREATE POLICY "Allow public read for first module" ON public.course_modules
    FOR SELECT USING (module_index = 0);

-- Policy 2: Allow paid/authorized users to read premium modules (index > 0).
-- Access requires an explicit grant row (course slug OR the all-access '*' flag).
CREATE POLICY "Allow read for paid users" ON public.course_modules
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.user_course_access
            WHERE user_course_access.user_id = auth.uid()
              AND user_course_access.course_slug IN (course_modules.course_slug, '*')
        )
    );
