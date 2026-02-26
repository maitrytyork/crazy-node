import os
import requests
import subprocess
from google import genai
from pathlib import Path

# =====================================
# 1️⃣ Validate Environment Variables
# =====================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PR_NUMBER = os.getenv("PR_NUMBER")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_BRANCH = os.getenv("PR_BRANCH")

if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER, REPO, PR_BRANCH]):
    raise Exception("❌ Missing required environment variables")

print("✅ Environment validated")
print(f"🔀 Working on branch: {PR_BRANCH}")

# =====================================
# 2️⃣ Initialize Gemini Client
# =====================================
client = genai.Client(api_key=GEMINI_API_KEY)
print("✅ Gemini client initialized")

# =====================================
# 3️⃣ Fetch PR Diff
# =====================================
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

# =====================================
# 4️⃣ Generate PR Intelligence Report
# =====================================
pr_prompt = f"""
You are an AI PR Intelligence Agent.

Analyze the following Pull Request diff and generate:

1. Executive Summary
2. Technical Summary
3. Change Classification
4. Risk Level (Low/Medium/High + score out of 10)
5. Architectural Impact
6. Suggested Test Cases

PR Diff:
{pr_diff}
"""

pr_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=pr_prompt
)

pr_report = pr_response.text
print("✅ PR intelligence generated")

# =====================================
# 5️⃣ Post PR Comment
# =====================================
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"

comment_res = requests.post(
    comment_url,
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    },
    json={"body": f"## 🤖 AI PR Intelligence Report\n\n{pr_report}"}
)

if comment_res.status_code == 201:
    print("✅ Comment posted")
else:
    print("⚠️ Failed to post comment:", comment_res.text)

# =====================================
# 6️⃣ Create PR Snapshot File
# =====================================
docs_path = Path("docs/pr-history")
docs_path.mkdir(parents=True, exist_ok=True)

snapshot_file = docs_path / f"pr-{PR_NUMBER}.md"
snapshot_file.write_text(
    f"# PR #{PR_NUMBER} Technical Snapshot\n\n{pr_report}"
)

print("✅ PR snapshot created")

# =====================================
# 7️⃣ Generate Full Project Architecture
# =====================================

def collect_source_files():
    code_content = ""
    for path in Path(".").rglob("*"):
        if path.suffix in [".ts", ".js", ".py", ".java", ".go", ".cs"]:
            if any(x in str(path) for x in ["node_modules", ".git", "docs"]):
                continue
            try:
                code_content += f"\n\n# File: {path}\n"
                code_content += path.read_text(encoding="utf-8")
            except:
                continue
    return code_content


full_codebase = collect_source_files()

architecture_prompt = f"""
You are a Senior Software Architect.

Analyze the entire project and generate a complete
System Architecture Document.

Include:
1. System Overview
2. Core Modules & Responsibilities
3. Architectural Pattern
4. Data Flow
5. Error Handling Strategy
6. Security Considerations
7. Scalability Considerations
8. Extension Points

Codebase:
{full_codebase}
"""

arch_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=architecture_prompt
)

architecture_doc = arch_response.text

architecture_file = Path("docs/architecture.md")
architecture_file.write_text(
    "# System Architecture\n\n" + architecture_doc
)

print("✅ architecture.md regenerated")

# =====================================
# 8️⃣ Commit & Push (SAFE VERSION)
# =====================================

try:
    # Ensure correct branch (fix detached HEAD issue)
    subprocess.run(["git", "checkout", PR_BRANCH], check=True)

    subprocess.run(["git", "config", "user.name", "ai-doc-bot"], check=True)
    subprocess.run(["git", "config", "user.email", "bot@ai-doc.local"], check=True)

    subprocess.run(["git", "add", "docs"], check=True)

    commit = subprocess.run(
        ["git", "commit", "-m", "docs: update architecture and PR snapshot"],
        capture_output=True,
        text=True
    )

    if commit.returncode != 0:
        print("⚠️ No changes to commit")
    else:
        print("✅ Commit created")

        push = subprocess.run(
            ["git", "push", "origin", PR_BRANCH],
            capture_output=True,
            text=True
        )

        if push.returncode != 0:
            print("❌ Push failed:")
            print(push.stderr)
            raise Exception("Push failed")
        else:
            print("✅ Push successful")

except subprocess.CalledProcessError as e:
    print("❌ Git command failed:", e)
    raise

print("🎉 Living Engineering Documentation System completed successfully!")