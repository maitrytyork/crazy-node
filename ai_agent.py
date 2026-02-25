import os
import requests
from google import genai

# ==============================
# 1️⃣ Validate Environment Variables
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PR_NUMBER = os.getenv("PR_NUMBER")
REPO = os.getenv("GITHUB_REPOSITORY")

if not GEMINI_API_KEY or not GITHUB_TOKEN or not PR_NUMBER or not REPO:
    raise Exception("❌ Missing required environment variables")

print("✅ Environment variables validated")

# ==============================
# 2️⃣ Initialize Gemini Client (NEW SDK)
# ==============================
client = genai.Client(api_key=GEMINI_API_KEY)
print("✅ Gemini client initialized")

# ==============================
# 3️⃣ Get PR Diff from GitHub API
# ==============================
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
response = requests.get(diff_url, headers=headers)

if response.status_code != 200:
    raise Exception(f"❌ Failed to fetch PR diff: {response.text}")

pr_diff = response.text
print("✅ PR diff fetched")

if not pr_diff.strip():
    print("⚠️ No changes found in PR.")
    exit(0)

# ==============================
# 4️⃣ Generate AI Documentation
# ==============================
prompt = f"""
You are an AI Documentation Agent.

Analyze the following GitHub Pull Request diff and generate:
- A concise PR summary
- Key changes
- Impact
- Suggested documentation updates (if needed)

PR Diff:
{pr_diff}
"""

try:
    ai_response = client.models.generate_content(
        model="gemini-2.0-flash",   # ✅ WORKING MODEL
        contents=prompt
    )

    documentation = ai_response.text
    print("✅ Documentation generated")

except Exception as e:
    print("Detailed API Error:", str(e))
    raise Exception(f"❌ Gemini API error: {str(e)}")

# ==============================
# 5️⃣ Post Comment to PR
# ==============================
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"

comment_data = {
    "body": f"## 🤖 AI Generated Documentation\n\n{documentation}"
}

comment_response = requests.post(comment_url, headers={
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}, json=comment_data)

if comment_response.status_code == 201:
    print("✅ Successfully commented on PR")
else:
    print("❌ Failed to comment:", comment_response.text)
    raise Exception("Failed to post PR comment")

print("🎉 AI Documentation Agent completed successfully!")