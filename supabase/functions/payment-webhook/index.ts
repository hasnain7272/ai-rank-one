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
      
      // Parse hex signature to byte array
      const hexToBytes = (hex: string) => {
        const bytes = new Uint8Array(hex.length / 2)
        for (let i = 0; i < hex.length; i += 2) {
          bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16)
        }
        return bytes
      }

      const isVerified = await crypto.subtle.verify(
        "HMAC", cryptoKey,
        hexToBytes(signature),
        new TextEncoder().encode(bodyText)
      )
      if (!isVerified) return new Response("Unauthorized signature", { status: 401 })
    }

    const payload = JSON.parse(bodyText)
    const eventName = payload.meta.event_name
    
    if (eventName === 'order_created') {
      const attributes = payload.data.attributes
      const email = attributes.customer_email
      const custom = payload.meta.custom_data || {}
      const variantId = String(attributes.variant_id ?? custom.variant_id ?? "")

      // Map the purchased variant to a grant type. Single-course purchases carry
      // the course slug via custom[course_slug] passed in the checkout link.
      const grant = await resolveGrant(variantId, custom.course_slug)

      console.log(`Processing purchase for: ${email}, grant: ${grant.type}${grant.courseSlug ? " (" + grant.courseSlug + ")" : ""}`)

      // 1. Create or get user
      let userId: string
      const { data: users, error: listError } = await supabase.auth.admin.listUsers()
      if (listError) throw listError
      
      const existingUser = users.users.find(u => u.email === email)
      if (existingUser) {
        userId = existingUser.id
      } else {
        const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
          email: email,
          email_confirm: true,
          user_metadata: { source: 'purchase' }
        })
        if (createError) throw createError
        userId = newUser.user.id
        await supabase.auth.admin.inviteUserByEmail(email)
      }

      // 2. Grant access
      if (grant.type === 'single' && grant.courseSlug) {
        await grantAccess(userId, grant.courseSlug)
      } else if (grant.type === 'bundle') {
        // Bundle grants a fixed set of 5 flagship courses.
        const BUNDLE_SLUGS = [
          'langgraph-multi-agents',
          'building-a-production-rag-system',
          'llm-fine-tuning-with-lora-and-qlora',
          'advanced-prompt-engineering-for-developers',
          'mlops-from-experiment-to-production',
        ]
        for (const slug of BUNDLE_SLUGS) await grantAccess(userId, slug)
      } else if (grant.type === 'all') {
        // All-access: mark the user as having access to every course via a flag row.
        const { error } = await supabase
          .from('user_course_access')
          .upsert({ user_id: userId, course_slug: '*' })
        if (error) throw error
      }
    }

    return new Response(JSON.stringify({ success: true }), { headers: { "Content-Type": "application/json" } })
  } catch (err) {
    console.error("Webhook processing error:", err)
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: { "Content-Type": "application/json" } })
  }
})

// Resolve which tier a purchase belongs to by matching the Lemon Squeezy variant id.
// Variant ids are injected from env (LEMON_VARIANT_SINGLE / _BUNDLE / _ALL).
async function resolveGrant(variantId: string, courseSlug?: string): Promise<{ type: 'single'|'bundle'|'all', courseSlug?: string }> {
  const single = Deno.env.get('LEMON_VARIANT_SINGLE') || ""
  const bundle = Deno.env.get('LEMON_VARIANT_BUNDLE') || ""
  const all = Deno.env.get('LEMON_VARIANT_ALL') || ""

  if (variantId && variantId === single) return { type: 'single', courseSlug }
  if (variantId && variantId === bundle) return { type: 'bundle' }
  if (variantId && variantId === all) return { type: 'all' }

  // Fallback: if no variant matched (e.g. env not set), default to single with provided slug.
  return { type: 'single', courseSlug: courseSlug || 'langgraph-multi-agents' }
}

async function grantAccess(userId: string, courseSlug: string) {
  const { error } = await supabase
    .from('user_course_access')
    .upsert({ user_id: userId, course_slug: courseSlug })
  if (error) throw error
  console.log(`Granted access to ${userId} for ${courseSlug}`)
}
