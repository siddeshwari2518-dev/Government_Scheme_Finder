# 🇮🇳 SchemeSaathi

### *Find every Indian government scheme you're eligible for — in seconds.*

> You fill in your details. Our AI searches official government sources, checks your eligibility,
> and hands you a step-by-step guide to apply.
> No jargon. No dead ends. Just your schemes, your rights.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Tavily](https://img.shields.io/badge/Tavily_Search-FF6B35?style=for-the-badge)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)

---

## 🔴 The Problem

India has **3,000+ government schemes** — for farmers, women, students, daily wage workers, and more.

Most eligible citizens **never apply.** Not because they don't need the help. But because:

```
❌  Schemes are scattered across dozens of government websites
❌  Eligibility is written in confusing legal language
❌  Citizens don't know which documents to bring
❌  There's no one place that says "this scheme is for YOU"
```

**SchemeSaathi fixes all of that.**

---

## ✅ What It Does

You enter your profile. The AI does the rest.

```
  You enter          →    AI searches       →    AI checks         →    You get
  your details            official sources        your eligibility       a guide to apply

  Age, income             gov.in, nic.in          "Yes, you qualify      Documents needed
  State, job              myscheme.gov.in          because..."           Steps to apply
  Category                In real time            Ranked by impact       Official links
  Special needs                                                          Helpline numbers
```

---

## 🤖 How The AI Works — 4 Agents

SchemeSaathi uses a **4-step AI agent pipeline.** Each agent has one job.

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│   👤 Your Profile                                          │
│   Age · Gender · State · Income · Job · Category          │
│                                                            │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  🔍  AGENT 1 — RESEARCHER                                  │
│                                                            │
│  Searches official government websites in real time        │
│  Sources: gov.in · nic.in · myscheme.gov.in               │
│  Only finds real, verifiable schemes. No guessing.         │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  ✅  AGENT 2 — ELIGIBILITY ANALYZER                        │
│                                                            │
│  Compares your profile against each scheme's criteria      │
│  Tells you exactly WHY you qualify (or don't)              │
│  Ranks schemes by how much benefit they give you           │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  📋  AGENT 3 — GUIDE WRITER                                │
│                                                            │
│  Writes a personalised application guide for each scheme   │
│  Includes: documents needed · steps · links · helplines    │
│  Written simply — as if explaining to a first-time user    │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  ⭐  AGENT 4 — JUDGE                                       │
│                                                            │
│  The AI checks its own work                                │
│  Scores on: Accuracy · Eligibility · Clarity · Relevance   │
│  Gives you a confidence score for the recommendations      │
└────────────────────────────────────────────────────────────┘
                        │
                        ▼
              🎯 Your Scheme Dashboard
```

---

## 📁 Project Structure

```
schemesaathi/
│
├── 🐍  app.py              →  Main Streamlit app & UI
├── 🤖  agents.py           →  All 4 AI agents + fallback logic
├── 💬  prompts.py          →  System prompts for each agent
│
├── 🚂  railway.toml        →  Railway deployment config
├── 📦  requirements.txt    →  Python dependencies
│
├── 🔒  .env                →  Your API keys (never share this)
├── 📄  .env.example        →  Template — shows what keys are needed
└── 🚫  .gitignore          →  Keeps .env out of GitHub
```

---

## 🚀 Run It Locally

**Step 1 — Clone the repo**
```bash
git clone https://github.com/yourusername/schemesaathi.git
cd schemesaathi
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Add your API keys**

Rename `.env.example` to `.env` and fill in your keys:
```
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

| Key | Where to get it | Cost |
|-----|----------------|------|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | Free tier available |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | Free tier available |

**Step 4 — Start the app**
```bash
streamlit run app.py
```

Then open → [http://localhost:8501](http://localhost:8501)

---

## 🚂 Deploy on Railway

**Step 1** — Push your code to GitHub *(make sure `.env` is in `.gitignore`)*

**Step 2** — Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub

**Step 3** — Add your environment variables in the Railway dashboard:
```
Variables tab → Add:
  GEMINI_API_KEY  =  your_key
  TAVILY_API_KEY  =  your_key
```

**Step 4** — Railway auto-detects `railway.toml` and deploys. Done ✅

> The `railway.toml` in this repo already has the correct start command configured.

---

## 👥 Who Is This For?

| Citizen | Schemes They Can Find |
|---------|----------------------|
| 🌾 **Farmer** | PM Kisan · Kisan Credit Card · Crop Insurance · Soil Health Card |
| 🏠 **Low-income family** | PMAY Housing · Ayushman Bharat · Ration Card schemes |
| 👩 **Woman** | PM Ujjwala · Maternity Benefit · Mahila Shakti schemes |
| 🎓 **Student** | Pre/Post Matric Scholarships for SC/ST/OBC/EWS/Minority |
| ♿ **Differently-abled** | ADIP Scheme · Disability Pension · Assistive devices |
| 💼 **Self-employed** | Mudra Loan · PMEGP · Startup India benefits |
| 👴 **Senior citizen** | Old Age Pension · Indira Gandhi National Old Age Pension |

---

## 🛠️ Tech Stack

| What | Technology |
|------|-----------|
| **UI** | Streamlit |
| **AI Agents** | Google Gemini 2.0 Flash |
| **Live Search** | Tavily Search API |
| **Deployment** | Railway |
| **Language** | Python 3.10+ |

---

## ⚠️ Important Disclaimer

This tool is **not an official government service.**
It is an AI assistant for informational purposes only.

Always verify scheme details and apply through official portals:

| Resource | Link |
|----------|------|
| 🌐 One-stop scheme finder | [myscheme.gov.in](https://myscheme.gov.in) |
| 🏛️ National portal | [india.gov.in](https://india.gov.in) |
| ☎️ Government helpline | 1800-11-8002 |

---

## 📄 License

MIT License — free to use, modify, and share.

---

<div align="center">

**Made for every Indian citizen who deserves to know their rights. 🇮🇳**

*If this helped you, give it a ⭐ on GitHub!*

</div>
