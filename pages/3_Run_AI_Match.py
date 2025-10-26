import streamlit as st
import pandas as pd
import sys
import os
from modules.translations import get_text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="AI Matching", layout="wide")

lang = st.session_state.get('language', 'en')

st.title("🎯 Run AI Match & Manage Invitations")

if 'recruiter' not in st.session_state:
    st.warning(get_text('error', lang) + ": Session not initialized. Please go back to the main page.")
    st.stop()
recruiter = st.session_state.recruiter

if not recruiter.job_postings or not recruiter.candidates:
    st.warning(get_text('get_started', lang))
    st.stop()

# --- Job Selection ---
job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
selected_job_title = st.selectbox(get_text('choose_job', lang), options=job_options.keys())
job_id = job_options[selected_job_title]

if st.button("🚀 Find Top Matches", type="primary"):
    with st.spinner("Running AI analysis on all candidates..."):
        top_matches = recruiter.generate_match_report(job_id, top_n=10)
        st.session_state.top_matches = top_matches  # Save matches to session state

if 'top_matches' in st.session_state:
    st.header(get_text('top_matched_candidates', lang))
    
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
                st.progress(int(match['score']), text=f"{get_text('match_score', lang)}: {match['score']}%")
                with st.expander(get_text('view_match_details', lang)):
                    st.write(f"**{get_text('strengths_label', lang)}:** Strong alignment in skills and experience.")
                    st.write(f"**{get_text('potential_label', lang)}:** High number of GitHub contributions and portfolio projects.")
                    st.write(f"**{get_text('gaps_label', lang)}:** Missing one non-critical skill.")

            with col2:
                status = candidate.get('status', 'Not Invited')
                st.metric(get_text('status', lang), status)

            with col3:
                if status == 'Not Invited':
                    if st.button(get_text('generate_invitation', lang), key=f"invite_{candidate_id}"):
                        # Build link dynamically based on current Streamlit server port
                        port = st.get_option("server.port") or 8501
                        base_url = f"http://localhost:{port}"
                        # app.py handles candidate view at root when 'cid' is present
                        test_link = f"{base_url}?cid={candidate_id}"
                        candidate['status'] = 'Invited'
                        candidate['test_link'] = test_link
                        st.success(get_text('invitation_generated', lang))
                        st.markdown(f"**{get_text('shareable_link', lang)}:**")
                        st.code(test_link)
                        st.experimental_rerun()
                elif status == 'Test Completed':
                    results = candidate.get('test_results', {})
                    st.success(get_text('test_completed_single', lang))
                    st.write(f"**Tech Score:** {results.get('technical_score', 'N/A')}%")
                    st.write(f"**Soft Skill Score:** {results.get('soft_skill_score', 'N/A')}%")
                    if results.get('cheating_flags', 0) > 0:
                        st.error(f"⚠️ Cheating Flags: {results['cheating_flags']}")
                else: # Invited
                    st.info(get_text('invitation_sent', lang))
                    st.code(candidate.get('test_link', ''))
