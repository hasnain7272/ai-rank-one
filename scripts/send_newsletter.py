import os
import json
import glob
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def send_weekly_newsletter():
    if not RESEND_API_KEY:
        print("⚠️ RESEND_API_KEY not configured. Skipping email send.")
        return
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("⚠️ Supabase credentials missing. Cannot fetch subscribers.")
        return

    # 1. Fetch latest newsletter file
    issues = glob.glob("newsletter/issues/*.html")
    if not issues:
        print("📭 No newsletter issues generated yet.")
        return
    latest_issue = max(issues) # Gets the latest date
    
    with open(latest_issue, "r", encoding="utf-8") as f:
        html_content = f.read()

    print(f"📧 Sending newsletter issue {latest_issue}...")

    # 2. Fetch subscriber list from Supabase using REST API
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/subscribers?select=email"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch subscribers from Supabase: {response.text}")
            return
            
        subscribers = response.json()
        emails = [s["email"] for s in subscribers]
        
        if not emails:
            print("📭 No active subscribers found.")
            return
            
        print(f"👥 Found {len(emails)} subscribers. Dispatching via Resend...")
        
        # 3. Dispatch emails one-by-one (or via Resend Batch API)
        resend_headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        for email in emails:
            data = {
                "from": "AI Rank One <noreply@airankone.com>",
                "to": email,
                "subject": "نشرة الذكاء الاصطناعي الأسبوعية 🚀",
                "html": html_content
            }
            res_response = requests.post("https://api.resend.com/emails", json=data, headers=resend_headers)
            if res_response.status_code == 200:
                print(f"  ✅ Sent successfully to: {email}")
            else:
                print(f"  ❌ Failed to send to {email}: {res_response.text}")
                
        print("🎉 Newsletter dispatch completed.")
    except Exception as e:
        print(f"❌ Error dispatching newsletter: {e}")

if __name__ == "__main__":
    send_weekly_newsletter()
