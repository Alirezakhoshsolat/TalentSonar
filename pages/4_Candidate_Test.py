import streamlit as st
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Skills Assessment", layout="centered")

# --- Anti-Cheating: Tab Focus Detection (Simulation) ---
# In a real app, you might use a more robust JS component.
if 'tab_hidden_count' not in st.session_state:
    st.session_state.tab_hidden_count = 0

# This is a placeholder to simulate detection.
# We can't truly detect tab switching from server-side Python,
# but we can add a button to simulate the effect.
if st.sidebar.button("Simulate switching tabs"):
    st.session_state.tab_hidden_count += 1
    st.toast("Warning: Navigating away from the test is monitored.", icon="⚠️")

# --- Initialization and Candidate Verification ---
try:
    query_params = st.experimental_get_query_params()
    candidate_id_str = query_params.get("cid", [None])[0]
    if candidate_id_str is None:
        st.error("Invalid test link. No candidate ID found.")
        st.stop()
    candidate_id = int(candidate_id_str)
    
    if 'recruiter' not in st.session_state:
        st.error("Session expired or invalid. Please use the link provided by the recruiter.")
        st.stop()
    
    recruiter = st.session_state.recruiter
    candidate = recruiter.get_candidate_by_id(candidate_id)

    if not candidate:
        st.error("Candidate not found. The link may be incorrect.")
        st.stop()

except (ValueError, IndexError):
    st.error("Invalid candidate ID in the URL.")
    st.stop()


st.title(f"Welcome, {candidate['name']}!")
st.markdown("This assessment consists of a technical challenge and a soft skills evaluation. You have **15 minutes** to complete it.")

# --- Anti-Cheating: Timer and State Management ---
if 'test_start_time' not in st.session_state:
    st.session_state.test_start_time = time.time()

time_limit_seconds = 15 * 60
elapsed_time = time.time() - st.session_state.test_start_time
remaining_time = time_limit_seconds - elapsed_time

if remaining_time <= 0:
    st.error("Time's up! Your answers have been submitted automatically.")
    # In a real app, you'd trigger the submission logic here.
    st.stop()

st.sidebar.metric("Time Remaining", f"{int(remaining_time // 60)}m {int(remaining_time % 60)}s")
st.sidebar.warning(f"Tab Switch Flags: {st.session_state.tab_hidden_count}")

# --- Technical Assessment ---
st.header("1. Technical Challenge")
st.code("Write a Python function to find the second largest number in a list of unique integers.")
code_solution = st.text_area("Your solution:", height=200, key="tech_code", placeholder="def second_largest(numbers):...")

# --- Soft Skills Assessment ---
st.header("2. Situational Judgement")
st.markdown("You discover a critical bug in production code written by a senior colleague just before a major release. What is your most immediate and crucial action?")
soft_skill_q1 = st.radio(
    "Choose your primary action:",
    (
        "Email the senior colleague and wait for a response.",
        "Fix the bug yourself and push the code directly.",
        "Document the bug and the fix, then privately and calmly inform the colleague to review and deploy it together.",
        "Announce the bug in the public team channel."
    ), index=None, key="soft_skill_q"
)

# --- Submission ---
if st.button("Submit Final Answers", type="primary"):
    # Grade the technical test (simulated)
    tech_score = 0
    if "sorted" in code_solution or "[-2]" in code_solution:
        tech_score = 85
    elif "max" in code_solution and "remove" in code_solution:
        tech_score = 95 # More efficient
    else:
        tech_score = 40

    # Grade the soft skills test
    soft_skill_score = 0
    if soft_skill_q1 and "privately and calmly" in soft_skill_q1:
        soft_skill_score = 95
    else:
        soft_skill_score = 30

    # Update candidate profile
    candidate['status'] = 'Test Completed'
    candidate['test_results'] = {
        'technical_score': tech_score,
        'soft_skill_score': soft_skill_score,
        'cheating_flags': st.session_state.tab_hidden_count,
        'completed_at': time.time()
    }
    
    st.success("Your assessment has been submitted! Thank you.")
    st.balloons()
    
    # Clean up session state for this test
    del st.session_state.test_start_time
    del st.session_state.tab_hidden_count
    st.info("You can now close this window.")
    st.stop()
