import os
import requests
from google import genai

# -------------------------------------------------
# 1️⃣ Configure Gemini (New SDK)
# -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found.")

client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------------------------
# 2️⃣ GitHub Environment Variables
# -------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

if not all([GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER]):
    raise ValueError("❌ Missing GitHub environment variables.")

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

diff_text = response.text

if not diff_text.strip():
    print("⚠ No changes detected.")
    exit(0)

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
6. Changelog entry

PR Diff:
{diff_text}
"""

# -------------------------------------------------
# 5️⃣ Call Gemini (FIXED MODEL NAME)
# -------------------------------------------------

try:
    # Changed from "gemini-1.5-flash-latest" to "gemini-1.5-flash"
    # This matches the expected format for the google-genai SDK
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )

    if not response or not response.text:
        ai_output = "⚠️ Gemini was unable to generate a response for this diff."
    else:
        ai_output = response.text

except Exception as e:
    # Captures specific API errors for debugging in GitHub Actions logs
    print(f"Detailed API Error: {str(e)}")
    raise Exception(f"❌ Gemini API error: {str(e)}")

# -------------------------------------------------
# 6️⃣ Post PR Comment
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

print("✅ AI documentation comment posted successfully.")