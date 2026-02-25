# 🚀 AI Dev Documentation Agent

Automatically converts Pull Request code changes into structured technical documentation and intelligent review insights.

---

## 🔥 What It Does

When a Pull Request is opened, this AI agent:

- 📄 Analyzes code changes
- 🧠 Generates technical documentation
- 🔍 Provides structured review feedback
- 📝 Creates changelog summaries
- 🤖 Posts AI-generated comments automatically on the PR

Fully automated using:
- GitHub Actions
- Google Gemini API
- Python

---

## ⚙️ How It Works

1. Developer opens a Pull Request
2. GitHub Action triggers automatically
3. Code diff is extracted
4. Gemini analyzes the changes
5. Structured documentation is generated
6. AI comment is posted on the PR

No manual documentation required.

---

## 📂 Project Structure

```
your-repo/
│
├── .github/
│   └── workflows/
│       └── ai-doc-agent.yml
│
├── ai_agent.py
└── README.md
```

---

## 🔐 Setup Instructions

### 1️⃣ Add Gemini API Key

Go to:

Repository → Settings → Secrets and variables → Actions

Add a new repository secret:

Name:
```
GEMINI_API_KEY
```

Value:
```
Your Google AI Studio API Key
```

---

### 2️⃣ Add Workflow File

Create:

```
.github/workflows/ai-doc-agent.yml
```

Add your workflow configuration.

---

### 3️⃣ Add AI Script

Create:

```
ai_agent.py
```

Place it in the root directory of the repository.

---

### 4️⃣ Open a Pull Request

Once a PR is opened, the AI Documentation Agent runs automatically.

You can monitor execution in:

Repository → Actions tab

---

## 🎯 Purpose

This project helps:

- Reduce manual documentation effort
- Improve Pull Request clarity
- Maintain structured changelogs
- Scale engineering knowledge sharing
- Support team-level development workflows

---

## 💡 Vision

Turn code into knowledge automatically.