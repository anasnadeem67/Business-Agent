# 🤖 Autonomous Business Agent
**Nexe-Agent Internship — Advanced Task 1**

An autonomous AI agent that performs multi-step business reasoning, task planning, and tool orchestration — with full execution logs.

---

## 📁 Project Structure

```
autonomous_business_agent/
├── .env                    ← Your API keys (never commit this)
├── .env.example            ← Template for .env
├── requirements.txt
├── agents/
│   └── business_agent.py   ← Core agentic loop (multi-step reasoning)
├── tools/
│   └── business_tools.py   ← All tool definitions + implementations
├── utils/
│   └── log_utils.py        ← Save/load execution logs
├── ui/
│   └── app.py              ← Streamlit frontend
└── logs/                   ← Auto-generated JSON execution logs
```

---

## ⚙️ Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API keys
cp .env.example .env
# Edit .env and add your keys

# 3. Run the app
streamlit run ui/app.py
```

---

## 🔑 .env Configuration

```env
OPENROUTER_API_KEY=sk-or-v1-...   # Your OpenRouter key
BASE_URL=https://openrouter.ai/api/v1
MODEL=poolside/laguna-m.1:free     # Change model here anytime
```

**To change model**, just update `MODEL` in `.env`. No code changes needed.

---

## 🧰 Available Tools

| Tool | Purpose |
|------|---------|
| `web_search` | DuckDuckGo real-time search |
| `calculate` | Safe math / financial calculations |
| `generate_report` | Structured business report template |
| `analyze_market` | SWOT, competitive, trend, customer analysis |
| `create_task_plan` | Break goals into phased action plans |
| `save_to_memory` | Store findings across agent steps |

---

## ✨ Features

- ✅ **Multi-step reasoning** — Agent thinks before acting
- ✅ **Task planning** — Breaks complex goals into steps
- ✅ **Execution logs** — Every tool call logged with timestamps
- ✅ **Multi-turn chat** — Full conversation memory
- ✅ **Configurable model** — Change via `.env`
- ✅ **Save logs** — JSON logs saved to `/logs`
- ✅ **Beautiful UI** — Dark theme Streamlit interface

---

## 🚀 Example Queries

- "Do a SWOT analysis for a new Pakistani e-commerce startup"
- "Calculate ROI if I invest PKR 500,000 with 18% annual return over 3 years"
- "Create a 30-day launch plan for a SaaS product targeting SMEs"
- "Analyze the competitive landscape for food delivery in Karachi"

---

*Built for Nexe-Agent Internship — Agentic AI Developer Role*
