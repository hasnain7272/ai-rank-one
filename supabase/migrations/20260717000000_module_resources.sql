-- Add curated resources (articles, papers, videos, podcasts) per module.
ALTER TABLE public.course_modules
    ADD COLUMN IF NOT EXISTS resources JSONB NOT NULL DEFAULT '[]'::jsonb;
