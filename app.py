"""
PROJECT NEXUS — Streamlit Web Interface
Autonomous Multi-Agent AI Problem Solver
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from config import SYSTEM_ATTRIBUTION, PROJECT_NAME, QUALITY_THRESHOLD
from models import AgentMessage, FinalReport
from orchestrator import run_research_stream, run_research
from memory.vector_store import ResearchMemory

st.set_page_config(
    page_title=f"{PROJECT_NAME} — Autonomous Multi-Agent AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(11, 15, 25, 0.85);
        backdrop-filter: blur(10px);
    }
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    .nexus-card {
        background: #131D31;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .nexus-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-planner { background: #4338CA; color: #E0E7FF; }
    .badge-researcher { background: #0E7490; color: #CFFAFE; }
    .badge-analyst { background: #047857; color: #D1FAE5; }
    .badge-critic { background: #B45309; color: #FEF3C7; }
    .badge-writer { background: #6D28D9; color: #EDE9FE; }
    .badge-system { background: #334155; color: #F1F5F9; }
    
    .footer-text {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        padding: 2rem 0;
        border-top: 1px solid #1E293B;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚡ PROJECT NEXUS")
    st.markdown(f"*{SYSTEM_ATTRIBUTION}*")
    st.markdown("---")
    
    st.markdown("### 🤖 Active Agent Fleet")
    st.markdown("""
    - **Dynamic Supervisor / Planner**: Autonomous task decomposition
    - **Web Researcher**: Multi-source empirical investigation
    - **Data Analyst**: Numerical benchmarking & charts
    - **Critic & Verifier**: Quality audit & revision loops
    - **Synthesizer / Writer**: Report & .docx generator
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ System Controls")
    auto_approve = st.checkbox("Auto-Approve Research Plan", value=True, help="Disable to enable Human-in-the-Loop checkpoint review.")
    enable_voice = st.checkbox("Enable Audio Narration Script", value=True)
    
    st.markdown("---")
    memory = ResearchMemory()
    try:
        mem_count = memory.collection.count() if memory.collection else 0
    except Exception:
        mem_count = 0
    st.metric("ChromaDB Memory Records", mem_count)


# Main Content Area
st.title("⚡ PROJECT NEXUS")
st.caption(f"Autonomous Multi-Agent AI Problem Solver | {SYSTEM_ATTRIBUTION}")

query = st.text_area(
    "Enter your complex problem statement, inquiry, or challenge:",
    placeholder="e.g., Conduct an in-depth strategic analysis of autonomous multi-agent systems in enterprise automation, including benchmarks and adoption risks.",
    height=100,
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    start_btn = st.button("🚀 Solve Problem", type="primary", use_container_width=True)

if start_btn and query.strip():
    status_container = st.container()
    progress_placeholder = st.empty()
    activity_placeholder = st.container()
    
    with status_container:
        st.info("Initiating dynamic LangGraph supervisor and specialized agent fleet...")
    
    events_log = []
    final_state = None
    
    try:
        # Run streaming execution
        for event_state in run_research_stream(query.strip(), auto_approve=auto_approve):
            final_state = event_state
            messages = event_state.get("agent_messages", [])
            
            with activity_placeholder:
                for msg in messages[-4:]:
                    agent_cls = f"badge-{msg.agent}" if msg.agent in ["planner", "researcher", "analyst", "critic", "writer"] else "badge-system"
                    st.markdown(
                        f"""<div class="nexus-card">
                            <span class="nexus-badge {agent_cls}">{msg.agent}</span>
                            <span style="color:#94A3B8; font-size:0.8rem; margin-left:8px;">{msg.timestamp[-8:]}</span>
                            <p style="margin-top:8px; margin-bottom:0;">{msg.message}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )
        
        status_container.success("✨ Autonomous Problem-Solving Workflow Completed Successfully!")
        
        # Display Final Output Tabs
        if final_state and final_state.get("final_report"):
            report: FinalReport = final_state["final_report"]
            tab_report, tab_data, tab_critic, tab_export = st.tabs(["📄 Final Solution Report", "📊 Data & Charts", "🛡️ Quality Verification", "💾 Export & Memory"])
            
            with tab_report:
                st.markdown(report.markdown)
            
            with tab_data:
                st.subheader("Quantitative Insights & Visualizations")
                insights = final_state.get("data_insights", [])
                if insights:
                    for ins in insights:
                        st.markdown(f"**Task:** {ins.sub_question}")
                        st.write(ins.analysis_summary)
                        for cp in ins.chart_paths:
                            if os.path.exists(cp):
                                st.image(cp, caption=f"Generated Chart by Analyst Agent ({SYSTEM_ATTRIBUTION})", use_container_width=True)
                else:
                    st.info("No numerical charts were requested for this run.")
            
            with tab_critic:
                st.subheader("Critic Agent Audit Log")
                critic_reviews = final_state.get("critic_reviews", [])
                if critic_reviews:
                    for cr in critic_reviews:
                        col_sc1, col_sc2 = st.columns([1, 3])
                        with col_sc1:
                            st.metric("Quality Verification Score", f"{cr.score:.1f}/100")
                        with col_sc2:
                            st.write(f"**Status:** {'Approved' if cr.is_approved else 'Revision Requested'}")
                            st.write(f"**Feedback:** {cr.revision_feedback}")
                        if cr.strengths:
                            st.markdown("**Validated Strengths:**")
                            for s in cr.strengths:
                                st.markdown(f"- {s}")
                else:
                    st.info("Critic review completed with direct approval.")
            
            with tab_export:
                st.subheader("Document Download & Session Persistence")
                docx_file = final_state.get("docx_path")
                if docx_file and os.path.exists(docx_file):
                    with open(docx_file, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label="📥 Download .docx Word Report",
                        data=file_bytes,
                        file_name=os.path.basename(docx_file),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                    )
                else:
                    st.warning("Docx report generation was bypassed.")
                    
                st.markdown(f"**Attribution:** {SYSTEM_ATTRIBUTION}")
                
    except Exception as e:
        st.error(f"Execution Error: {e}")

st.markdown(f"<div class='footer-text'>{SYSTEM_ATTRIBUTION} • {PROJECT_NAME}</div>", unsafe_allow_html=True)
