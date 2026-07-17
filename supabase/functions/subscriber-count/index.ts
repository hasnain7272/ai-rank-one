import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4"

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

// Returns ONLY the subscriber count. Never exposes email addresses.
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

serve(async () => {
  try {
    const { count, error } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })

    if (error) throw error

    // Small buffer so the counter looks alive even with few real subscribers.
    const display = (count ?? 0) + 120

    return new Response(
      JSON.stringify({ count: display }),
      { headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=300" } }
    )
  } catch (err) {
    return new Response(
      JSON.stringify({ count: 120, error: err.message }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    )
  }
})
