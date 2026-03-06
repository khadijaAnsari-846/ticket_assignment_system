import streamlit as st
import requests
import time
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURATION ---
API_BASE_URL = "http://127.0.0.1:5000"

# --- UI CONFIG ---
st.set_page_config(page_title="Agentic Sprint Planner", page_icon="📅", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .log-text { font-family: 'Source Code Pro', monospace; color: #2e7d32; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "last_log_idx" not in st.session_state:
    st.session_state.last_log_idx = 0
if "session_start_dt" not in st.session_state:
    st.session_state.session_start_dt = datetime.now()
if "session_stats" not in st.session_state:
    st.session_state.session_stats = {}
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Data Ingestion")
    cv_files = st.file_uploader("Upload Developer CVs", type=["pdf"], accept_multiple_files=True)
    project_files = st.file_uploader("Upload Project Docs", type=["pdf"], accept_multiple_files=True)

    st.divider()
    generate_btn = st.button("🚀 Generate Weekly Plan", type="primary", use_container_width=True)

    # Live Clock
    duration_placeholder = st.empty()
    elapsed = datetime.now() - st.session_state.session_start_dt
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_placeholder.info(f"⏱️ Active: {hours:02d}:{minutes:02d}:{seconds:02d}")

    # Capacity View
    if st.session_state.session_stats:
        st.subheader("👥 Current Capacity")
        for dev, hrs in st.session_state.session_stats.items():
            st.write(f"**{dev}**: {hrs}/35h")
            st.progress(min(hrs/35, 1.0))

    st.divider()
    if st.button("🔄 Reset Session", use_container_width=True):
        requests.post(f"{API_BASE_URL}/reset-session")
        st.session_state.clear()
        st.rerun()

# --- MAIN LOGIC ---
st.title("👨‍💼 CrewAI Sprint Planner")

if generate_btn:
    if not cv_files or not project_files:
        st.error("Upload both files!")
    else:
        files = []
        for f in cv_files: files.append(('cv_files', (f.name, f.getvalue(), 'application/pdf')))
        for f in project_files: files.append(('project_files', (f.name, f.getvalue(), 'application/pdf')))

        resp = requests.post(f"{API_BASE_URL}/generate-plan", files=files)
        if resp.status_code == 200:
            st.session_state.job_id = resp.json().get("job_id")
            st.session_state.last_log_idx = 0
            st.rerun()

# --- POLLING AREA ---
if st.session_state.job_id:
    job_id = st.session_state.job_id
    progress_bar = st.progress(0)
    log_window = st.container(border=True, height=300)

    while True:
        res = requests.get(f"{API_BASE_URL}/status/{job_id}").json()
        status = res.get("status")

        if "session_status" in res:
            st.session_state.session_stats = res.get("session_status")

        logs = res.get("progress_logs", [])
        with log_window:
            for log in logs[st.session_state.last_log_idx:]:
                st.markdown(f"<div class='log-text'>{log}</div>", unsafe_allow_html=True)
            st.session_state.last_log_idx = len(logs)

        if status == "Completed":
            st.session_state.last_result = res.get("result")
            st.session_state.job_id = None
            st.rerun()
            break
        elif status == "Failed":
            st.error("Agents failed to generate plan.")
            st.session_state.job_id = None
            break

        time.sleep(2)
        st.rerun()

# --- DISPLAY RESULTS & FEEDBACK (LEARNING SECTION) ---


# This handles the result display AND the Feedback/Learning form
if st.session_state.get("last_result"):
    res = st.session_state.last_result
    st.divider()

    tabs = st.tabs(["📅 Schedule", "📝 Raw Data", "🤖 Train Agent"])

    with tabs[0]:
        assignments = res.get('assignments') or res.get('developers') or []
        if not assignments:
            st.warning("⚠️ All developers are currently occupied. No tasks assigned.")
        else:
            for dev in assignments:
                name = dev.get('developer_name') or dev.get('developer') or "Developer"
                with st.expander(f"Assignments for {name}"):
                    st.table(pd.DataFrame(dev.get('schedule', [])))

    with tabs[1]:
        st.json(res)

    with tabs[2]:
        st.subheader("🧠 Knowledge Feedback")
        st.write("Correct the agent so it allocates better next time.")

        with st.form("feedback_form"):
            col1, col2 = st.columns(2)
            with col1:
                t_rating = st.select_slider("Timing", ["Short", "Perfect", "Long"], "Perfect")
                c_rating = st.radio("Complexity", ["Simple", "Accurate", "Complex"], 1)
            with col2:
                note = st.text_area("What should the agent remember?", placeholder="Ex: Alison is full for the week.")

            if st.form_submit_button("Submit & Learn"):
                payload = {"timing": t_rating, "complexity": c_rating, "note": note}
                if requests.post(f"{API_BASE_URL}/learn", json=payload).status_code == 200:
                    st.success("The Agent has learned this insight!")
                    st.balloons()

# The "Ticking" refresh logic
if st.session_state.job_id is None:
    time.sleep(1)
    st.rerun()
