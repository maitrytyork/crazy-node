import os
import requests
from google import genai
from google.genai import types

# -------------------------------------------------
# 1️⃣ Environment Variables
# -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found.")

if not all([GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER]):
    raise ValueError("❌ Missing GitHub environment variables.")

print("✅ Environment variables validated")

# -------------------------------------------------
# 2️⃣ Initialize Gemini Client (AI Studio Compatible)
# -------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(api_version="v1")
)

print("✅ Gemini client initialized")

# -------------------------------------------------
# 3️⃣ Fetch PR Diff
# -------------------------------------------------

diff_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

response = requests.get(diff_url, headers=headers)

if response.status_code != 200:
    raise Exception(f"❌ Failed to fetch PR diff: {response.text}")

diff_text = response.text.strip()

if not diff_text:
    print("⚠ No changes detected.")
    exit(0)

print("✅ PR diff fetched")

# Limit diff size for safety
MAX_CHARS = 15000
if len(diff_text) > MAX_CHARS:
    diff_text = diff_text[:MAX_CHARS]
    print("⚠ Diff truncated due to size")

# -------------------------------------------------
# 4️⃣ Prompt
# -------------------------------------------------

prompt = f"""
You are a senior software architect.

Analyze the following Pull Request diff and provide:

1. Summary of changes
2. Technical explanation
3. Impact analysis
4. Risks
5. Suggested documentation updates
6. Changelog entry (Markdown format)

PR Diff:
{diff_text}
"""

# -------------------------------------------------
# 5️⃣ Call Gemini (Stable Model)
# -------------------------------------------------

try:
    response = client.models.generate_content(
        model="gemini-1.0-pro",
        contents=prompt,
    )

    ai_output = response.text if response and response.text else \
        "⚠️ Gemini could not generate a response."

    print("✅ Gemini response generated")

except Exception as e:
    print(f"Detailed API Error: {str(e)}")
    raise Exception(f"❌ Gemini API error: {str(e)}")

# -------------------------------------------------
# 6️⃣ Post Comment to PR
# -------------------------------------------------

comment_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues/{PR_NUMBER}/comments"

comment_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

comment_body = {
    "body": f"## 🤖 AI Documentation Agent Report\n\n{ai_output}"
}

comment_response = requests.post(comment_url, json=comment_body, headers=comment_headers)

if comment_response.status_code != 201:
    raise Exception(f"❌ Failed to post PR comment: {comment_response.text}")

print("🚀 AI documentation comment posted successfully.")