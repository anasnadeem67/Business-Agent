"""
ui/app.py  —  Autonomous Business Agent  |  Nexe-Agent Internship Task
Run: streamlit run ui/app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.business_agent import run_agent, ExecutionLog, get_model
from utils.log_utils import save_log, list_logs, load_log
from tools.business_tools import get_memory

st.set_page_config(
    page_title="Autonomous Business Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #f8fafc; color: #1e293b; }

.main-header {
    background: linear-gradient(90deg, #1d4ed8, #0891b2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px #1d4ed820;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.main-header h1 { font-size: 2rem; font-weight: 700; color: #fff; margin: 0; }
.main-header p { color: #bfdbfe; margin: 0.25rem 0 0; font-size: 0.95rem; }

.chat-user {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px 12px 4px 12px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    margin-left: 10%;
    box-shadow: 0 2px 8px #1d4ed810;
}
.chat-assistant {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px 12px 12px 4px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    margin-right: 5%;
    box-shadow: 0 2px 8px #00000008;
}

.exec-log {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #7dd3a8;
    max-height: 400px;
    overflow-y: auto;
}

.status-badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-active { background: #dcfce7; border: 1px solid #86efac; color: #166534; }
.badge-model  { background: #dbeafe; border: 1px solid #93c5fd; color: #1e40af; }

.tool-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    box-shadow: 0 1px 4px #00000008;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

.stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #0891b2) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #1d4ed830 !important;
}

hr { border-color: #e2e8f0 !important; }

[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 1px 4px #00000008;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:      st.session_state.messages = []
if "exec_logs" not in st.session_state:     st.session_state.exec_logs = []
if "total_steps" not in st.session_state:   st.session_state.total_steps = 0
if "total_queries" not in st.session_state: st.session_state.total_queries = 0
if "pending_input" not in st.session_state: st.session_state.pending_input = ""

st.markdown("""
<div class="main-header">
    <div style="font-size:3rem;">🤖</div>
    <div>
        <h1>Autonomous Business Agent</h1>
        <p>Multi-step reasoning · Task planning · Execution logs &nbsp;|&nbsp; Nexe-Agent Internship — Advanced Task</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    model = get_model()
    st.markdown(f"""
    <span class="status-badge badge-active">● ACTIVE</span>&nbsp;
    <span class="status-badge badge-model">🧠 {model.split('/')[-1]}</span>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    col1.metric("Queries", st.session_state.total_queries)
    col2.metric("Tool Steps", st.session_state.total_steps)
    st.markdown("---")
    st.markdown("### 🔧 Available Tools")
    tools_info = [
        ("🔍","web_search","Search internet"),
        ("🧮","calculate","Financial math"),
        ("📄","generate_report","Create reports"),
        ("📊","analyze_market","SWOT & analysis"),
        ("📋","create_task_plan","Task planning"),
        ("💾","save_to_memory","Agent memory"),
    ]
    for icon, name, desc in tools_info:
        st.markdown(f"""
        <div class="tool-card">
            {icon} <b style="color:#1e293b;">{name}</b><br>
            <span style="color:#64748b;font-size:0.8rem;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    memory = get_memory()
    if memory:
        st.markdown("### 🧠 Agent Memory")
        for k, v in memory.items():
            with st.expander(f"🔑 {k}"):
                st.caption(v[:300])
    st.markdown("---")
    st.markdown("### 📁 Saved Run Logs")
    saved = list_logs()
    if saved:
        for log_meta in saved[:5]:
            with st.expander(f"📝 {log_meta['timestamp']} ({log_meta['steps']} steps)"):
                st.caption(f"Query: {log_meta['query']}")
                if st.button("Load", key=f"load_{log_meta['file']}"):
                    data = load_log(log_meta["path"])
                    st.json(data)
    else:
        st.caption("No logs saved yet.")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.exec_logs = []
        st.rerun()

st.markdown("#### 💡 Try an example:")
examples = [
    "Do a SWOT analysis for a new Pakistani e-commerce startup",
    "Calculate ROI if I invest PKR 500,000 with 18% annual return over 3 years",
    "Create a 30-day launch plan for a SaaS product targeting SMEs",
    "Search for latest AI business trends in 2025 and summarize",
    "Analyze the competitive landscape for a food delivery app in Karachi",
]
cols = st.columns(len(examples))
for i, (col, ex) in enumerate(zip(cols, examples)):
    with col:
        if st.button(ex[:35] + "…", key=f"ex_{i}"):
            st.session_state.pending_input = ex
            st.rerun()

chat_col, log_col = st.columns([3, 2])

with chat_col:
    st.markdown("### 💬 Conversation")
    with st.container():
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <b style="color:#1d4ed8;">👤 You</b><br>
                    <span style="color:#1e293b;">{msg["content"]}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <b style="color:#0891b2;">🤖 Agent</b><br>
                    <span style="color:#1e293b;">{msg["content"]}</span>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("---")
    user_input = st.text_area(
        "Your business query:",
        value=st.session_state.pending_input,
        placeholder="Ask me anything about your business — strategy, analysis, planning, calculations...",
        height=100,
        key="user_input",
    )
    run_col, clear_col = st.columns([3, 1])
    with run_col:
        submit = st.button("🚀 Run Agent", use_container_width=True)
    with clear_col:
        if st.button("🔄 New", use_container_width=True):
            st.session_state.pending_input = ""
            st.rerun()

with log_col:
    st.markdown("### ⚙️ Execution Log")
    log_placeholder = st.empty()
    if st.session_state.exec_logs:
        latest_log = st.session_state.exec_logs[-1]
        with log_placeholder.container():
            st.markdown(f"""
            <div class="exec-log">
            {"<br>".join([
                f"<b style='color:#60a5fa;'>[{e['timestamp']}] Step {e['step']}</b> — "
                f"<span style='color:#f59e0b;'>{e['type'].upper()}</span>"
                + (f" | 🔧 {e['tool']}" if e['tool'] else "")
                + f"<br><span style='color:#94a3b8;'>{e['content'][:200].replace(chr(10), ' ')}</span>"
                for e in latest_log.entries
            ])}
            </div>
            """, unsafe_allow_html=True)
        if st.button("💾 Save This Log"):
            if st.session_state.messages:
                last_q = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "query")
                path = save_log(latest_log.entries, last_q)
                st.success(f"Saved: {os.path.basename(path)}")
    else:
        log_placeholder.markdown("""
        <div class="exec-log" style="color:#64748b;">
        ● Waiting for agent to run...<br>
        Each tool call and reasoning step will appear here in real time.
        </div>
        """, unsafe_allow_html=True)

if submit:
    query = st.session_state.get("user_input", "").strip()
    if query:
        st.session_state.pending_input = ""
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        status_box = st.empty()
        log = ExecutionLog()
        updates = []

        def yield_update(msg: str):
            updates.append(msg)
            status_box.info("  ·  ".join(updates[-3:]))

        with st.spinner("🤖 Agent is working..."):
            try:
                final_answer = run_agent(query, history, log, yield_update)
            except Exception as e:
                final_answer = f"❌ Agent error: {str(e)}"

        status_box.empty()
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        st.session_state.exec_logs.append(log)
        st.session_state.total_queries += 1
        st.session_state.total_steps += len(log.entries)
        st.rerun()
