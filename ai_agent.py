import os
import requests
import google.generativeai as genai

# =========================
# 1. Configure Gemini
# =========================

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# =========================
# 2. Read Git Diff
# =========================

with open("pr_diff.txt", "r", encoding="utf-8") as f:
    diff = f.read()

if not diff.strip():
    print("No changes detected.")
    exit()

# =========================
# 3. Prepare Prompt
# =========================

prompt = f"""
You are a senior software architect and technical documentation expert.

Analyze the following git diff and generate:

1. Change Type
2. Technical Summary
3. API Changes
4. Breaking Changes
5. Risk Level (Low/Medium/High)
6. Code Review Feedback
7. Markdown Technical Documentation
8. Changelog Entry

Be structured and professional.

GIT DIFF:
{diff}
"""

# =========================
# 4. Call Gemini
# =========================

response = model.generate_content(prompt)
output = response.text

# =========================
# 5. Post Comment to PR
# =========================

repo = os.getenv("GITHUB_REPOSITORY")

# Example: refs/pull/5/merge
ref = os.getenv("GITHUB_REF")
pr_number = ref.split("/")[2]

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

headers = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3+json"
}

data = {
    "body": output
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    print("Comment posted successfully.")
else:
    print("Failed to post comment:", response.text)