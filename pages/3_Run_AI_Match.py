import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="AI Matching", layout="wide")

st.title("🎯 Run AI Match & Manage Invitations")

if 'recruiter' not in st.session_state:
    st.warning("Session not initialized. Please go back to the main page.")
    st.stop()
recruiter = st.session_state.recruiter

if not recruiter.job_postings or not recruiter.candidates:
    st.warning("Please add jobs and candidates first from the respective pages.")
    st.stop()

# --- Job Selection ---
job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
selected_job_title = st.selectbox("Select a Job Posting to find matches for:", options=job_options.keys())
job_id = job_options[selected_job_title]

if st.button("🚀 Find Top Matches", type="primary"):
    with st.spinner("Running AI analysis on all candidates..."):
        top_matches = recruiter.generate_match_report(job_id, top_n=10)
        st.session_state.top_matches = top_matches  # Save matches to session state

if 'top_matches' in st.session_state:
    st.header("Top Matched Candidates")
    
    for match in st.session_state.top_matches:
        candidate_id = match['candidate_id']
        candidate = recruiter.get_candidate_by_id(candidate_id)
        
        if not candidate:
            continue

        with st.container():
            st.divider()
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.subheader(f"{candidate['name']}")
                st.progress(int(match['score']), text=f"Match Score: {match['score']}%")
                with st.expander("View Match Details (Explainable AI)"):
                    st.write(f"**Strengths:** Strong alignment in skills and experience.")
                    st.write(f"**Potential:** High number of GitHub contributions and portfolio projects.")
                    st.write(f"**Gaps:** Missing one non-critical skill.")

            with col2:
                status = candidate.get('status', 'Not Invited')
                st.metric("Status", status)

            with col3:
                if status == 'Not Invited':
                    if st.button("✉️ Invite to Test", key=f"invite_{candidate_id}"):
                        test_link = f"http://localhost:8501/Candidate_Test?cid={candidate_id}"
                        candidate['status'] = 'Invited'
                        candidate['test_link'] = test_link
                        st.success(f"Invitation sent to {candidate['name']}!")
                        st.info(f"Shareable Link: {test_link}")
                        st.experimental_rerun()
                elif status == 'Test Completed':
                    results = candidate.get('test_results', {})
                    st.success("✅ Test Completed")
                    st.write(f"**Tech Score:** {results.get('technical_score', 'N/A')}%")
                    st.write(f"**Soft Skill Score:** {results.get('soft_skill_score', 'N/A')}%")
                    if results.get('cheating_flags', 0) > 0:
                        st.error(f"⚠️ Cheating Flags: {results['cheating_flags']}")
                else: # Invited
                    st.info("✉️ Invitation Sent")
                    st.code(candidate.get('test_link', ''))
