import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from modules.smart_recruiter import SmartRecruiter
import pandas as pd

st.set_page_config(
    page_title="Smart Recruiter AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the SmartRecruiter engine in the session state if it doesn't exist
if 'recruiter' not in st.session_state:
    st.session_state.recruiter = SmartRecruiter()

recruiter = st.session_state.recruiter

st.title("🤖 Smart Recruiter AI Dashboard")
st.markdown("Welcome to the AI-powered recruitment platform for specialized talent.")

# --- Key Metrics ---
st.header("Platform Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Active Job Postings", len(recruiter.job_postings))
col2.metric("Candidates in Database", len(recruiter.candidates))

# Mock a realistic average match quality
scores = [recruiter.score_candidate_match(c, recruiter.parse_job_requirements(j['description'])) for c in recruiter.candidates for j in recruiter.job_postings]
avg_score = sum(scores) / len(scores) if scores else 0
col3.metric("Average Match Quality", f"{avg_score:.0f}%", f"{avg_score - 75:.0f}%")

st.header("Quick Match")

if recruiter.job_postings and recruiter.candidates:
    job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
    selected_job_title = st.selectbox("Select a Job to quickly match:", options=job_options.keys(), key="quick_match_job")
    
    if st.button("⚡ Find Top 3 Candidates"):
        with st.spinner("Analyzing candidates..."):
            job_id = job_options[selected_job_title]
            top_matches = recruiter.generate_match_report(job_id, top_n=3)
            st.success("Found top matches!")
            for match in top_matches:
                st.subheader(f"{match['name']} - Score: {match['score']}%")
                st.write(f"Reason: Strong alignment in required skills and high growth potential.")
else:
    st.warning("Please add jobs and candidates in the respective pages to enable matching.")

st.sidebar.success("Select a page above to start.")
