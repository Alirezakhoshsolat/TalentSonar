import streamlit as st
import pandas as pd
import random
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from talentsonar.config import settings

st.set_page_config(page_title="Manage Candidates", layout="wide")

st.title("👥 Manage Candidates")

if 'recruiter' not in st.session_state:
    st.warning("Session not initialized. Please go back to the main page.")
    st.stop()
recruiter = st.session_state.recruiter

# --- Feature 1: Upload Candidates from CSV ---
st.header("Upload New Candidates")
uploaded_file = st.file_uploader("Choose a CSV file with candidate data", type="csv")
if uploaded_file is not None:
    try:
        new_candidates_df = pd.read_csv(uploaded_file)
        # Basic validation
        required_cols = ['id', 'name', 'skills', 'years_experience']
        if all(col in new_candidates_df.columns for col in required_cols):
            new_candidates = new_candidates_df.to_dict('records')
            recruiter.candidates.extend(new_candidates)
            st.success(f"Successfully imported {len(new_candidates)} candidates!")
        else:
            st.error(f"CSV must contain the following columns: {', '.join(required_cols)}")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

# --- Feature 2: Discover Unconventional Candidates (REAL) ---
st.header("Discover Unconventional Talent")

if recruiter.job_postings:
    job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
    selected_job_title = st.selectbox(
        "Select a job to find candidates for:", 
        options=job_options.keys(),
        key="discovery_job_select"
    )
    
    if st.button("🔍 Discover Candidates from GitHub for this Job"):
        if not settings.GEMINI_API_KEY:
            st.error("Gemini API Key not configured. Please add it to your .env file to analyze the job.")
        elif not settings.GITHUB_TOKEN:
            st.error("GitHub Token not configured. Please add it to your .env file to search for candidates.")
        else:
            job_id = job_options[selected_job_title]
            with st.spinner(f"Analyzing job and searching GitHub for experts..."):
                try:
                    new_candidates = recruiter.discover_unconventional_candidates(job_id)
                    if new_candidates:
                        st.success(f"Discovered and added {len(new_candidates)} new high-potential candidates!")
                    else:
                        st.warning("Could not find any new candidates for that job's requirements.")
                except Exception as e:
                    st.error(f"An error occurred during discovery: {e}")
else:
    st.warning("Please add a job posting on the 'Manage Job Postings' page first.")



# --- Feature 3: View All Candidates ---
st.header("Candidate Database")
if recruiter.candidates:
    # Create a DataFrame for display
    df = pd.DataFrame(recruiter.candidates)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No candidates in the database yet.")
