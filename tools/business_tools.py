"""
tools/business_tools.py
All tools available to the Autonomous Business Agent
"""
import json
import datetime
import math
import re
from typing import Any


# ─────────────────────────────────────────────
# TOOL DEFINITIONS  (OpenAI SDK format)
# ─────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, news, market data, competitor analysis, or any business-related query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations, financial projections, ROI analysis, profit margins, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A safe mathematical expression to evaluate, e.g. '(1000 * 0.15) + 500'"
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable description of what is being calculated"
                    }
                },
                "required": ["expression", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generate a structured business report or summary document for a given topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the report"
                    },
                    "sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of section headings to include in the report"
                    },
                    "context": {
                        "type": "string",
                        "description": "Background context or data to include in the report"
                    }
                },
                "required": ["title", "sections", "context"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_market",
            "description": "Analyze market trends, SWOT analysis, or competitive landscape for a business or product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {
                        "type": "string",
                        "description": "Name of the business or product to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["swot", "competitive", "trend", "customer"],
                        "description": "Type of market analysis to perform"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry or sector of the business"
                    }
                },
                "required": ["business_name", "analysis_type", "industry"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task_plan",
            "description": "Break down a complex business goal into structured actionable tasks with priorities and timelines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "The high-level business goal to plan for"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for the plan, e.g. '30 days', '1 quarter'"
                    },
                    "resources": {
                        "type": "string",
                        "description": "Available resources or constraints"
                    }
                },
                "required": ["goal", "timeframe"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_memory",
            "description": "Save important findings, decisions, or data to agent memory for use in later steps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "A short identifier key for this memory entry"
                    },
                    "value": {
                        "type": "string",
                        "description": "The content to remember"
                    }
                },
                "required": ["key", "value"]
            }
        }
    }
]


# ─────────────────────────────────────────────
# TOOL EXECUTOR
# ─────────────────────────────────────────────

# In-process memory store
_memory: dict[str, str] = {}


def execute_tool(tool_name: str, tool_args: dict) -> Any:
    """Route and execute a tool call, return result string."""

    if tool_name == "web_search":
        return _web_search(tool_args["query"])

    elif tool_name == "calculate":
        return _calculate(tool_args["expression"], tool_args.get("description", ""))

    elif tool_name == "generate_report":
        return _generate_report(
            tool_args["title"],
            tool_args["sections"],
            tool_args["context"]
        )

    elif tool_name == "analyze_market":
        return _analyze_market(
            tool_args["business_name"],
            tool_args["analysis_type"],
            tool_args["industry"]
        )

    elif tool_name == "create_task_plan":
        return _create_task_plan(
            tool_args["goal"],
            tool_args.get("timeframe", "30 days"),
            tool_args.get("resources", "standard")
        )

    elif tool_name == "save_to_memory":
        return _save_to_memory(tool_args["key"], tool_args["value"])

    else:
        return f"❌ Unknown tool: {tool_name}"


# ─────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────

def _web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=4):
                results.append(f"• {r['title']}\n  {r['body']}\n  🔗 {r['href']}")
        if results:
            return f"🔍 Web Search Results for: '{query}'\n\n" + "\n\n".join(results)
        return f"No results found for: {query}"
    except Exception as e:
        return f"Web search failed: {str(e)}"


def _calculate(expression: str, description: str) -> str:
    try:
        # Safe evaluation - allow only math operations
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round, "min": min, "max": max})
        # Strip unsafe characters
        safe_expr = re.sub(r"[^0-9+\-*/().% ]", "", expression)
        result = eval(safe_expr, {"__builtins__": {}}, allowed)
        return (
            f"🧮 Calculation: {description}\n"
            f"   Expression : {expression}\n"
            f"   Result     : {result:,.4f}"
        )
    except Exception as e:
        return f"Calculation error: {e}"


def _generate_report(title: str, sections: list, context: str) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"📄 BUSINESS REPORT",
        f"{'='*50}",
        f"Title   : {title}",
        f"Date    : {now}",
        f"{'='*50}",
        "",
        "CONTEXT / BACKGROUND",
        "-" * 30,
        context,
        "",
    ]
    for i, section in enumerate(sections, 1):
        lines.append(f"{i}. {section.upper()}")
        lines.append("-" * 30)
        lines.append(f"[Section '{section}' — to be filled with analysis data]")
        lines.append("")
    lines.append("=" * 50)
    lines.append("END OF REPORT")
    return "\n".join(lines)


def _analyze_market(business_name: str, analysis_type: str, industry: str) -> str:
    templates = {
        "swot": f"""
📊 SWOT ANALYSIS — {business_name} ({industry})
{'='*50}
STRENGTHS
  • Core competency in {industry}
  • Established brand / unique value proposition
  • Operational efficiency

WEAKNESSES
  • Resource or capital constraints
  • Limited market reach
  • Potential skill gaps

OPPORTUNITIES
  • Growing demand in {industry}
  • Digital transformation trends
  • Untapped customer segments

THREATS
  • Competitive pressure
  • Regulatory changes in {industry}
  • Economic uncertainty
""",
        "competitive": f"""
🏆 COMPETITIVE ANALYSIS — {business_name} ({industry})
{'='*50}
Positioning : Mid-market leader in {industry}
Key Rivals  : Top 3-5 players in {industry}
Differentiators:
  • Unique product/service features
  • Pricing strategy
  • Customer experience
Gap Analysis:
  • Areas where {business_name} leads
  • Areas requiring improvement
""",
        "trend": f"""
📈 MARKET TREND ANALYSIS — {industry}
{'='*50}
Current Trends:
  • Digitalization & AI adoption
  • Consumer preference shifts
  • Regulatory evolution
Growth Forecast : +12–18% YoY (estimated)
Emerging Niches : Sustainability, personalization
Risk Factors    : Supply chain, inflation
""",
        "customer": f"""
👥 CUSTOMER ANALYSIS — {business_name}
{'='*50}
Target Segments:
  • Primary : B2B / B2C decision-makers
  • Secondary : Early adopters
Pain Points : Cost, efficiency, reliability
Buying Behavior : Research-driven, price-sensitive
Retention Levers: Quality, support, loyalty programs
"""
    }
    return templates.get(analysis_type, "Analysis type not recognized.")


def _create_task_plan(goal: str, timeframe: str, resources: str) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"""
📋 TASK PLAN
{'='*50}
Goal      : {goal}
Timeframe : {timeframe}
Resources : {resources}
Created   : {now}
{'='*50}

PHASE 1 — RESEARCH & DISCOVERY (Week 1)
  ☐ Define success metrics and KPIs
  ☐ Conduct market & competitor research
  ☐ Identify stakeholders and dependencies

PHASE 2 — STRATEGY & PLANNING (Week 2)
  ☐ Develop detailed action roadmap
  ☐ Allocate budget and resources
  ☐ Set milestones and checkpoints

PHASE 3 — EXECUTION (Week 3–4)
  ☐ Launch core initiatives
  ☐ Monitor progress against KPIs
  ☐ Iterate based on feedback

PHASE 4 — REVIEW & OPTIMIZE (End of {timeframe})
  ☐ Measure outcomes vs goals
  ☐ Document lessons learned
  ☐ Plan next iteration

Priority Legend: 🔴 High  🟡 Medium  🟢 Low
"""


def _save_to_memory(key: str, value: str) -> str:
    _memory[key] = value
    return f"✅ Saved to memory: [{key}] = {value[:80]}{'...' if len(value) > 80 else ''}"


def get_memory() -> dict:
    return dict(_memory)
