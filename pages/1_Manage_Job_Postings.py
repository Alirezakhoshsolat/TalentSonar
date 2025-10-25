import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Manage Jobs", layout="wide")

st.title("📝 Manage Job Postings")

# Access the recruiter engine from session state
if 'recruiter' not in st.session_state:
    st.warning("Session not initialized. Please go back to the main page.")
    st.stop()
recruiter = st.session_state.recruiter

with st.form("new_job_form"):
    st.header("Add a New Job Posting")
    job_title = st.text_input("Job Title")
    job_description = st.text_area("Paste Job Description Here", height=250)
    submitted = st.form_submit_button("Analyze and Save Job")

    if submitted:
        if job_title and job_description:
            new_job = {'title': job_title, 'description': job_description}
            recruiter.job_postings.append(new_job)
            st.success(f"Successfully saved job: {job_title}")
        else:
            st.error("Please provide both a title and a description.")

st.header("Current Job Postings")
if recruiter.job_postings:
    for i, job in enumerate(recruiter.job_postings):
        with st.expander(f"**{job['title']}**"):
            st.markdown(job['description'])
else:
    st.info("No job postings have been added yet.")
