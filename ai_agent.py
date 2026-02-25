import os
import requests
import google.generativeai as genai

# -------------------------------------------------
# 1️⃣ Configure Gemini
# -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Free tier safe model
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------------------------
# 2️⃣ Get GitHub Environment Variables
# -------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

if not GITHUB_TOKEN:
    raise ValueError("❌ GITHUB_TOKEN not found.")

if not GITHUB_REPOSITORY:
    raise ValueError("❌ GITHUB_REPOSITORY not found.")

if not PR_NUMBER:
    raise ValueError("❌ PR_NUMBER not found.")

# -------------------------------------------------
# 3️⃣ Fetch PR Diff from GitHub API
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
    print("⚠ No changes detected in PR.")
    exit(0)

# -------------------------------------------------
# 4️⃣ Prepare Prompt for AI
# -------------------------------------------------

prompt = f"""
You are a senior software architect reviewing a Pull Request.

Analyze the following PR diff and provide:

1. 📌 Summary of changes
2. 🛠 Technical explanation
3. 📈 Impact analysis
4. ⚠ Potential risks or concerns
5. 📖 Suggested documentation updates
6. 🧾 Changelog entry

Be clear, structured, and professional.

Pull Request Diff:
{diff_text}
"""

# -------------------------------------------------
# 5️⃣ Generate AI Response
# -------------------------------------------------

try:
    ai_response = model.generate_content(prompt)
    ai_output = ai_response.text
except Exception as e:
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

print("✅ AI documentation comment posted successfully.")