import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4"

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const DODO_WEBHOOK_SECRET = Deno.env.get('DODO_WEBHOOK_SECRET')

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

async function verify(secret: string, body: string, headers: Headers): Promise<boolean> {
  const id = headers.get("webhook-id")
  const timestamp = headers.get("webhook-timestamp")
  const signatureHeader = headers.get("webhook-signature")
  if (!id || !timestamp || !signatureHeader) return false

  const now = Math.floor(Date.now() / 1000)
  const reqTime = parseInt(timestamp, 10)
  if (isNaN(reqTime) || Math.abs(now - reqTime) > 300) return false

  const cleanSecret = secret.startsWith("whsec_") ? secret.substring(6) : secret
  const binarySecret = Uint8Array.from(atob(cleanSecret), c => c.charCodeAt(0))

  const cryptoKey = await crypto.subtle.importKey(
    "raw", binarySecret, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  )
  const toSign = `${id}.${timestamp}.${body}`
  const signature = await crypto.subtle.sign("HMAC", cryptoKey, new TextEncoder().encode(toSign))
  const expectedBase64 = btoa(String.fromCharCode(...new Uint8Array(signature)))
  const expectedHex = Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, "0")).join("")

  return signatureHeader.split(" ").some(sig => {
    if (!sig.startsWith("v1,")) return false
    const val = sig.substring(3)
    return val === expectedBase64 || val === expectedHex
  })
}

serve(async (req) => {
  try {
    const bodyText = await req.text()
    if (DODO_WEBHOOK_SECRET && !(await verify(DODO_WEBHOOK_SECRET, bodyText, req.headers))) {
      return new Response("Unauthorized signature", { status: 401 })
    }

    const payload = JSON.parse(bodyText)
    if (payload.type === 'payment.succeeded') {
      const email = payload.data.customer.email
      const courseSlug = payload.data.metadata?.course_slug || "langgraph-multi-agents"

      console.log(`Processing purchase: ${email} -> ${courseSlug}`)

      let userId: string
      const { data: users, error: listError } = await supabase.auth.admin.listUsers()
      if (listError) throw listError
      
      const existingUser = users.users.find(u => u.email === email)
      if (existingUser) {
        userId = existingUser.id
      } else {
        const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
          email: email, email_confirm: true, user_metadata: { source: 'purchase' }
        })
        if (createError) throw createError
        userId = newUser.user.id
        await supabase.auth.admin.inviteUserByEmail(email)
      }

      const { error: accessError } = await supabase
        .from('user_course_access')
        .upsert({ user_id: userId, course_slug: courseSlug })

      if (accessError) throw accessError
      console.log(`Granted access to ${email} for ${courseSlug}`)
    }

    return new Response(JSON.stringify({ success: true }), { headers: { "Content-Type": "application/json" } })
  } catch (err) {
    console.error("Webhook error:", err)
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: { "Content-Type": "application/json" } })
  }
})
