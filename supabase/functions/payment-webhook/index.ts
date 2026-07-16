import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4"

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const LEMON_SQUEEZY_WEBHOOK_SECRET = Deno.env.get('LEMON_SQUEEZY_WEBHOOK_SECRET')

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

serve(async (req) => {
  try {
    const bodyText = await req.text()
    
    // Optional: Webhook signature verification (if secret configured)
    if (LEMON_SQUEEZY_WEBHOOK_SECRET) {
      const cryptoKey = await crypto.subtle.importKey(
        "raw", new TextEncoder().encode(LEMON_SQUEEZY_WEBHOOK_SECRET),
        { name: "HMAC", hash: "SHA-256" }, false, ["verify"]
      )
      const signature = req.headers.get("x-signature") || ""
      const isVerified = await crypto.subtle.verify(
        "HMAC", cryptoKey,
        new Uint8Array(Array.from(signature, c => c.charCodeAt(0))),
        new TextEncoder().encode(bodyText)
      )
      if (!isVerified) return new Response("Unauthorized signature", { status: 401 })
    }

    const payload = JSON.parse(bodyText)
    const eventName = payload.meta.event_name
    
    if (eventName === 'order_created') {
      const attributes = payload.data.attributes
      const email = attributes.customer_email
      // Lemon Squeezy allows custom meta data in checkout links (e.g., custom[course_slug]=langgraph)
      const courseSlug = payload.meta.custom_data?.course_slug || "langgraph-multi-agents"

      console.log(`Processing purchase for: ${email}, course: ${courseSlug}`)

      // 1. Create or get user
      let userId: string
      const { data: users, error: listError } = await supabase.auth.admin.listUsers()
      if (listError) throw listError
      
      const existingUser = users.users.find(u => u.email === email)
      if (existingUser) {
        userId = existingUser.id
      } else {
        // Invite/Create user instantly (sends email magic link via custom SMTP configured in Resend)
        const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
          email: email,
          email_confirm: true,
          user_metadata: { source: 'purchase' }
        })
        if (createError) throw createError
        userId = newUser.user.id

        // Send an invitation email to set password or login
        await supabase.auth.admin.inviteUserByEmail(email)
      }

      // 2. Grant access
      const { error: accessError } = await supabase
        .from('user_course_access')
        .upsert({ user_id: userId, course_slug: courseSlug })

      if (accessError) throw accessError
      console.log(`Successfully granted access to ${email} for ${courseSlug}`)
    }

    return new Response(JSON.stringify({ success: true }), { headers: { "Content-Type": "application/json" } })
  } catch (err) {
    console.error("Webhook processing error:", err)
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: { "Content-Type": "application/json" } })
  }
})
