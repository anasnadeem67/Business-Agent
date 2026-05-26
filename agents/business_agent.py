"""
agents/business_agent.py
Autonomous Business Agent — multi-step reasoning, task planning, execution logs
Uses OpenAI SDK with Groq backend
"""

import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CLIENT SETUP
# ─────────────────────────────────────────────

def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("BASE_URL", "https://api.groq.com/openai/v1"),
    )

def get_model() -> str:
    return os.getenv("MODEL", "llama-3.3-70b-versatile")


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an Autonomous Business Agent — an expert AI consultant specializing in business strategy, market analysis, financial planning, and operational excellence.

## YOUR CAPABILITIES
You have access to these tools:
- **web_search** — search the internet for real-time business data
- **calculate** — perform financial calculations, ROI, projections
- **generate_report** — create structured business reports
- **analyze_market** — SWOT, competitive, trend, customer analysis
- **create_task_plan** — break goals into actionable plans with timelines
- **save_to_memory** — store key findings for use in later steps

## YOUR OPERATING PRINCIPLES
1. **Multi-Step Reasoning** — Think through problems deeply before acting.
2. **Task Planning** — Always plan your steps before executing.
3. **Tool Orchestration** — Use multiple tools in sequence to build comprehensive answers.
4. **Execution Transparency** — Explain what you are doing and why at each step.
5. **Business Focus** — Every response should be actionable, data-driven, and valuable.

## RESPONSE FORMAT
When given a complex business task:
1. Start with **🧠 REASONING** — your analysis of the problem
2. Show **📋 PLAN** — the steps you will take
3. Execute tools and show **⚙️ EXECUTION** — what each tool returned
4. End with **✅ FINAL ANSWER** — synthesized, actionable insights

Be concise but thorough. Always provide business value."""


# ─────────────────────────────────────────────
# EXECUTION LOG
# ─────────────────────────────────────────────

class ExecutionLog:
    def __init__(self):
        self.entries: list[dict] = []
        self.start_time = datetime.datetime.now()

    def add(self, step_type: str, content: str, tool_name: str = None, tool_args: dict = None):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "step": len(self.entries) + 1,
            "type": step_type,
            "tool": tool_name,
            "args": tool_args,
            "content": content,
        }
        self.entries.append(entry)
        return entry

    def to_markdown(self) -> str:
        lines = [
            f"## 📊 Execution Log",
            f"*Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ]
        for e in self.entries:
            icon = {"reasoning": "🧠", "tool_call": "🔧", "tool_result": "📤", "response": "✅"}.get(e["type"], "•")
            lines.append(f"**Step {e['step']}** `{e['timestamp']}` {icon} **{e['type'].upper()}**")
            if e["tool"]:
                lines.append(f"> Tool: `{e['tool']}`")
                if e["args"]:
                    lines.append(f"> Args: `{json.dumps(e['args'], ensure_ascii=False)[:200]}`")
            lines.append(e["content"][:500] + ("..." if len(e["content"]) > 500 else ""))
            lines.append("")
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        lines.append(f"*Total steps: {len(self.entries)} | Elapsed: {elapsed:.1f}s*")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# FALLBACK: Direct answer without tools
# ─────────────────────────────────────────────

def run_agent_no_tools(
    user_message: str,
    chat_history: list[dict],
    log: ExecutionLog,
    yield_updates,
) -> str:
    """Fallback direct answer mode when tool calling is unavailable."""
    client = get_client()
    model = get_model()

    log.add("reasoning", f"Model '{model}' — using direct reasoning mode (no tool calls)")
    yield_updates("🧠 Agent analyzing your request...")

    direct_prompt = SYSTEM_PROMPT + """

## IMPORTANT — DIRECT MODE
You do NOT have function-calling available right now. Instead:
- Simulate tool usage by reasoning through each step manually
- Show your reasoning with 🧠 REASONING, 📋 PLAN, ⚙️ EXECUTION (simulated), ✅ FINAL ANSWER sections
- For calculations, show your math step by step
- For market analysis, provide structured SWOT/competitive analysis from your knowledge
- For task plans, create detailed phased plans
- Be thorough and actionable — give real business value
"""

    messages = [{"role": "system", "content": direct_prompt}]
    messages += chat_history
    messages.append({"role": "user", "content": user_message})

    yield_updates("💭 Generating comprehensive response...")

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=0.4,
    )

    answer = response.choices[0].message.content or "⚠️ No response from model."
    log.add("response", answer)
    yield_updates("✅ Done!")
    return answer


# ─────────────────────────────────────────────
# MAIN AGENT RUNNER
# ─────────────────────────────────────────────

def run_agent(
    user_message: str,
    chat_history: list[dict],
    log: ExecutionLog,
    yield_updates,
) -> str:
    from tools.business_tools import TOOLS, execute_tool

    client = get_client()
    model = get_model()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += chat_history
    messages.append({"role": "user", "content": user_message})

    log.add("reasoning", f"User request received: {user_message[:200]}")
    yield_updates("🧠 Agent is analyzing your request...")

    for iteration in range(10):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=2048,
                temperature=0.3,
            )
        except Exception as e:
            err = str(e)
            # If tool calling not supported, fall back to direct mode
            if "tool" in err.lower() or "function" in err.lower() or "400" in err:
                log.add("reasoning", f"Tool calling not supported: {err} — switching to direct mode")
                yield_updates("⚠️ Switching to direct reasoning mode...")
                return run_agent_no_tools(user_message, chat_history, log, yield_updates)
            raise

        msg = response.choices[0].message

        # Model wants to call tools
        if msg.tool_calls:
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                log.add("tool_call", f"Calling tool: {tool_name}", tool_name, tool_args)
                yield_updates(f"🔧 Using tool: **{tool_name}** ...")

                tool_result = execute_tool(tool_name, tool_args)

                log.add("tool_result", tool_result, tool_name)
                yield_updates(f"📤 Tool `{tool_name}` completed.")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(tool_result),
                })

        # Final text response
        else:
            final_text = msg.content or ""
            if not final_text.strip():
                log.add("reasoning", "Empty response from model — switching to direct mode")
                return run_agent_no_tools(user_message, chat_history, log, yield_updates)
            log.add("response", final_text)
            return final_text

    # Max iterations reached
    log.add("reasoning", "Max iterations reached — falling back to direct mode")
    return run_agent_no_tools(user_message, chat_history, log, yield_updates)
