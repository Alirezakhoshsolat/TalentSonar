"""
TalentSonar - Comprehensive Smart Recruiting Platform
Advanced AI-powered talent discovery and assessment system
"""

import streamlit as st
import sys
import os
import pandas as pd
import json
from datetime import datetime
import time
import io

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from modules.smart_recruiter import SmartRecruiter
from talentsonar.config import settings
from talentsonar.src.document_parser import DocumentParser
from talentsonar.src.candidate_tests import test_system
from modules.translations import get_text, get_language_selector

# File paths for data persistence
TEST_RESULTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'test_results.json')
CANDIDATES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'candidates_data.json')
JOB_POSTINGS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'job_postings.json')
DISCOVERED_CANDIDATES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'discovered_candidates.json')

# Helper functions for data persistence
def load_test_results():
    """Load test results from file."""
    try:
        if os.path.exists(TEST_RESULTS_FILE):
            with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading test results: {e}")
    return []

def load_job_postings():
    """Load job postings from file."""
    try:
        if os.path.exists(JOB_POSTINGS_FILE):
            with open(JOB_POSTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading job postings: {e}")
    return []

def save_job_postings(job_postings):
    """Save job postings to file."""
    try:
        os.makedirs(os.path.dirname(JOB_POSTINGS_FILE), exist_ok=True)
        with open(JOB_POSTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(job_postings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving job postings: {e}")
        return False

def load_discovered_candidates():
    """Load discovered candidates from file."""
    try:
        if os.path.exists(DISCOVERED_CANDIDATES_FILE):
            with open(DISCOVERED_CANDIDATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading discovered candidates: {e}")
    return []

def save_discovered_candidates(candidates):
    """Save discovered candidates to file."""
    try:
        os.makedirs(os.path.dirname(DISCOVERED_CANDIDATES_FILE), exist_ok=True)
        with open(DISCOVERED_CANDIDATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving discovered candidates: {e}")
        return False
    except Exception as e:
        print(f"Error loading test results: {e}")
    return []

def save_test_result(candidate_id, candidate_data, test_results, session_data):
    """Save a test result to file."""
    try:
        results = load_test_results()
        
        # Create result entry
        result_entry = {
            'candidate_id': candidate_id,
            'name': candidate_data.get('name', 'Unknown'),
            'email': candidate_data.get('email', 'N/A'),
            'phone': candidate_data.get('phone', 'N/A'),
            'linkedin': candidate_data.get('linkedin', 'N/A'),
            'location': candidate_data.get('location', 'N/A'),
            'github_username': candidate_data.get('username', 'N/A'),
            'status': 'Test Completed',
            'test_submitted_at': datetime.now().isoformat(),
            'test_results': test_results,
            'session_data': {
                'soft_skill_questions': session_data.get('soft_skill_questions', []),
                'technical_questions': session_data.get('technical_questions', []),
                'answers': session_data.get('answers', {})
            }
        }
        
        # Remove old entry if exists
        results = [r for r in results if r.get('candidate_id') != candidate_id]
        
        # Add new entry
        results.append(result_entry)
        
        # Save to file
        os.makedirs(os.path.dirname(TEST_RESULTS_FILE), exist_ok=True)
        with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving test result: {e}")
        return False

def load_candidates_data():
    """Load all candidates data from file."""
    try:
        if os.path.exists(CANDIDATES_FILE):
            with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading candidates data: {e}")
    return []

def save_candidates_data(candidates):
    """Save all candidates data to file."""
    try:
        os.makedirs(os.path.dirname(CANDIDATES_FILE), exist_ok=True)
        with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving candidates data: {e}")
        return False

# Page configuration
st.set_page_config(
    page_title="TalentSonar - Smart Recruiting Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🎯"
)

# Custom CSS for styling (minimal - let Streamlit handle colors)
st.markdown("""
    <style>
    /* Tab styling */
    button[data-baseweb="tab"] {
        height: 50px !important;
        padding: 0 24px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        border-radius: 8px 8px 0 0 !important;
        margin-right: 4px !important;
    }
    
    /* Active tab */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Anti-cheat indicator */
    .anti-cheat-active {
        position: fixed;
        top: 70px;
        right: 20px;
        background-color: #ff4444;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        z-index: 1000;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for complete data persistence
def init_session_state():
    """Initialize all session state variables to ensure data persistence."""
    if 'recruiter' not in st.session_state:
        st.session_state.recruiter = SmartRecruiter()
        # Load saved job postings
        saved_jobs = load_job_postings()
        if saved_jobs:
            st.session_state.recruiter.job_postings = saved_jobs
        
        # Load discovered candidates from file
        discovered_candidates = load_discovered_candidates()
        if discovered_candidates:
            # Add to recruiter.candidates, avoiding duplicates
            existing_ids = {c['id'] for c in st.session_state.recruiter.candidates}
            for candidate in discovered_candidates:
                if candidate['id'] not in existing_ids:
                    st.session_state.recruiter.candidates.append(candidate)
        
        # Sync candidate statuses with test results from file
        test_results = load_test_results()
        if test_results:
            completed_ids = {result['candidate_id'] for result in test_results}
            for candidate in st.session_state.recruiter.candidates:
                if candidate['id'] in completed_ids:
                    # Find the test result for this candidate
                    result_data = next((r for r in test_results if r['candidate_id'] == candidate['id']), None)
                    if result_data:
                        candidate['status'] = 'Test Completed'
                        candidate['test_results'] = result_data.get('test_results', {})
                        candidate['test_submitted_at'] = result_data.get('test_submitted_at', '')
    
    if 'discovered_candidates' not in st.session_state:
        st.session_state.discovered_candidates = {}  # job_id -> [candidate_ids]
        
        # Rebuild the mapping from candidates' job_id field
        for candidate in st.session_state.recruiter.candidates:
            job_id = candidate.get('job_id')
            
            # For backwards compatibility: assign candidates without job_id to the last job
            # (most likely they were just discovered)
            if job_id is None and len(st.session_state.recruiter.job_postings) > 0:
                job_id = len(st.session_state.recruiter.job_postings) - 1
                candidate['job_id'] = job_id  # Update the candidate
            
            if job_id is not None:
                if job_id not in st.session_state.discovered_candidates:
                    st.session_state.discovered_candidates[job_id] = []
                if candidate['id'] not in st.session_state.discovered_candidates[job_id]:
                    st.session_state.discovered_candidates[job_id].append(candidate['id'])
    
    if 'job_analysis_cache' not in st.session_state:
        st.session_state.job_analysis_cache = {}  # job_id -> analysis_dict
    
    if 'selected_job_id' not in st.session_state:
        st.session_state.selected_job_id = None
    
    if 'candidate_scores' not in st.session_state:
        st.session_state.candidate_scores = {}  # (job_id, candidate_id) -> detailed_scores
    
    if 'test_sessions' not in st.session_state:
        st.session_state.test_sessions = {}  # session_id -> session_data
    
    if 'document_parser' not in st.session_state:
        st.session_state.document_parser = DocumentParser()

init_session_state()
recruiter = st.session_state.recruiter

# Language selector
lang = get_language_selector()

# Check if this is candidate view (has candidate ID in URL)
query_params = st.query_params
candidate_id_param = query_params.get('cid', None)
session_id_param = query_params.get('sid', None)

# ====================================================================================
# CANDIDATE VIEW - Show ONLY the test page, no tabs/dashboard
# ====================================================================================
if candidate_id_param or session_id_param:
    # Minimal header for candidate
    st.title(get_text('candidate_portal', lang))
    st.markdown(get_text('candidate_subtitle', lang))
    st.divider()
    
    # Get candidate ID
    if session_id_param:
        # From existing session
        session_id = session_id_param
        if session_id in test_system.test_sessions:
            session_data = test_system.test_sessions[session_id]
            cand_id = session_data['candidate_id']
        else:
            st.error(get_text('session_not_found', lang))
            st.stop()
    else:
        # From URL parameter
        try:
            cand_id = int(candidate_id_param)
        except (ValueError, TypeError):
            st.error(get_text('invalid_cid_format', lang))
            st.stop()
    
    # Get candidate data
    candidate = recruiter.get_candidate_by_id(cand_id)
    if not candidate:
        st.error(f"❌ Invalid candidate ID: {cand_id}")
        st.info(get_text('total_candidates_system', lang).format(count=len(recruiter.candidates)))
        if recruiter.candidates:
            st.info(get_text('available_ids', lang).format(ids=[c.get('id') for c in recruiter.candidates[:5]]))
        st.stop()
    
    # CHECK LOGIN STATUS
    if f'logged_in_{cand_id}' not in st.session_state:
        # Show login form
        st.markdown(f"### {get_text('login_required', lang)}")
        st.info(get_text('login_subtitle', lang))
        
        with st.form("login_form"):
            col_user, col_pass = st.columns(2)
            with col_user:
                username_input = st.text_input(get_text('username', lang), placeholder="candidate_XXX")
            with col_pass:
                password_input = st.text_input(get_text('password', lang), type="password", placeholder=get_text('password', lang))
            
            login_submitted = st.form_submit_button(get_text('login_button', lang), type="primary", width="stretch")
            
            if login_submitted:
                # Verify credentials
                expected_username = candidate.get('username', f'candidate_{cand_id}')
                expected_password = candidate.get('password', '')
                
                if not expected_password:
                    st.error(get_text('not_invited_contact_hr', lang))
                    with st.expander(get_text('debug_info', lang)):
                        st.write(f"Candidate ID: {cand_id}")
                        st.write(f"Candidate Name: {candidate.get('name', 'Unknown')}")
                        st.write(f"Status: {candidate.get('status', 'Not Set')}")
                        st.write(f"Has Username: {bool(candidate.get('username'))}")
                        st.write(f"Has Password: {bool(candidate.get('password'))}")
                elif username_input == expected_username and password_input == expected_password:
                    st.session_state[f'logged_in_{cand_id}'] = True
                    st.success(get_text('login_success_redirect', lang))
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(get_text('invalid_credentials', lang))
                    with st.expander(get_text('hint', lang)):
                        st.write(get_text('expected_username_format', lang).format(id=cand_id))
                        st.write(get_text('password_case_sensitive', lang))
        
        st.stop()  # Don't show test until logged in
    
    # LOGGED IN - Show test
    col_welcome, col_logout = st.columns([4, 1])
    with col_welcome:
        st.success(f"✅ {get_text('welcome', lang)}: {candidate.get('name')}")
    with col_logout:
        if st.button(get_text('logout_button', lang), key="candidate_logout"):
            del st.session_state[f'logged_in_{cand_id}']
            if 'personal_info_submitted' in st.session_state:
                del st.session_state['personal_info_submitted']
            st.rerun()
    
    # CANDIDATE VIEW - Taking the test
    st.markdown(f"### {get_text('candidate_assessment_portal', st.session_state.get('test_language', lang) if 'test_language' in st.session_state else lang)}")
    
    # STEP 1: Language Selection for Test (separate from HR view language)
    if 'test_language' not in st.session_state:
        st.markdown(f"## {get_text('select_test_language', lang)}")
        st.info(get_text('test_language_prompt', lang))
        
        col_lang1, col_lang2 = st.columns(2)
        with col_lang1:
            if st.button("🇬🇧 English", key="test_lang_en", use_container_width=True, type="primary"):
                st.session_state.test_language = 'en'
                st.rerun()
        with col_lang2:
            if st.button("🇮🇹 Italiano", key="test_lang_it", use_container_width=True, type="primary"):
                st.session_state.test_language = 'it'
                st.rerun()
        
        st.stop()  # Don't proceed until language is selected
    
    # Get the test language (not the HR language)
    test_lang = st.session_state.test_language
    
    if session_id_param:
        # Resume existing session
        session_id = session_id_param
        session_data = test_system.test_sessions[session_id]
        st.info(get_text('continue_assessment', test_lang))
    else:
        # New session - will be created after personal info
        st.info(get_text('candidate_subtitle', test_lang))
        session_id = None
    
    # Personal Information Form
    if 'personal_info_submitted' not in st.session_state:
        st.subheader(get_text('personal_info', test_lang))
        
        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input(get_text('full_name', test_lang) + "*", value=candidate.get('name', ''))
                email = st.text_input(get_text('email', test_lang) + "*", value=candidate.get('email', ''))
            with col2:
                phone = st.text_input(get_text('phone', test_lang) + "*")
                location = st.text_input(get_text('current_location', test_lang), value=candidate.get('location', ''))
            
            linkedin = st.text_input(get_text('linkedin', test_lang))
            
            submitted = st.form_submit_button(get_text('submit_info', test_lang) + " →", type="primary", width="stretch")
            
            if submitted:
                if full_name and email and phone:
                    # Store personal info in session
                    st.session_state.personal_info = {
                        'name': full_name,
                        'email': email,
                        'phone': phone,
                        'location': location,
                        'linkedin': linkedin
                    }
                    st.session_state.personal_info_submitted = True
                    
                    # Create test session and store session_id
                    job_id = 0  # Default job for now
                    if recruiter.job_postings:
                        job_requirements = recruiter.job_postings[job_id].get('analysis', {})
                        session_id = test_system.create_test_session(candidate_id=cand_id, job_requirements=job_requirements)
                        st.session_state.test_session_id = session_id
                    
                    st.rerun()
                else:
                    st.error(get_text('fill_required_fields', test_lang))
    
    else:
        # Show test questions
        st.subheader(get_text('assessment_test', test_lang))
        
        # Get or create test session
        if 'test_session_id' not in st.session_state:
            job_id = 0
            job_requirements = recruiter.job_postings[job_id].get('analysis', {}) if recruiter.job_postings else {}
            session_id = test_system.create_test_session(candidate_id=cand_id, job_requirements=job_requirements)
            st.session_state.test_session_id = session_id
        else:
            session_id = st.session_state.test_session_id
        
        session_data = test_system.test_sessions[session_id]
        soft_questions = session_data['soft_skill_questions']
        tech_questions = session_data['technical_questions']
        all_questions = soft_questions + tech_questions
        
        # Anti-cheat monitoring
        st.markdown(f"""
            <div class="anti-cheat-active">
                🔒 {get_text('anti_cheat_active', test_lang)}
            </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        total_questions = len(all_questions)
        answered = len(session_data.get('answers', {}))
        progress = answered / total_questions if total_questions > 0 else 0
        
        st.progress(progress, text=get_text('progress_text', test_lang).format(answered=answered, total=total_questions))
        
        # Display questions
        st.markdown("---")
        st.markdown(f"#### {get_text('soft_skills_questions', test_lang)}")
        
        for i, question in enumerate(soft_questions):
            q_id = question['id']
            
            # Translate question text and options
            question_text = get_text(q_id, test_lang)
            st.markdown(f"**{get_text('question', test_lang)} {i+1}:** {question_text}")
            
            if question['type'] == 'multiple_choice':
                # Multiple choice question
                current_answer_dict = session_data.get('answers', {}).get(q_id)
                # Extract the actual answer value from the dict
                if current_answer_dict and isinstance(current_answer_dict, dict):
                    current_answer = current_answer_dict.get('answer')
                else:
                    current_answer = None
                
                # Translate options
                translated_options = []
                for idx in range(len(question['options'])):
                    option_key = f"{q_id}_o{idx+1}"
                    translated_options.append(get_text(option_key, test_lang))
                
                answer_idx = st.radio(
                    get_text('select_your_answer', test_lang) + ":",
                    options=range(len(translated_options)),
                    format_func=lambda x: translated_options[x],
                    key=f"soft_{q_id}",
                    index=current_answer if current_answer is not None else None
                )
                
                if answer_idx is not None and answer_idx != current_answer:
                    test_system.submit_answer(session_id, q_id, answer_idx)
                    st.rerun()
            
            elif question['type'] == 'text':
                # Text answer
                current_answer_dict = session_data.get('answers', {}).get(q_id)
                # Extract the actual answer value from the dict
                if current_answer_dict and isinstance(current_answer_dict, dict):
                    current_answer = current_answer_dict.get('answer', '')
                else:
                    current_answer = ''
                
                answer = st.text_area(
                    get_text('your_answer_min_words', test_lang).format(min_words=question.get('min_words', 20)) + ":",
                    value=current_answer,
                    key=f"soft_{q_id}",
                    height=100
                )
                
                if answer and answer != current_answer:
                    word_count = len(answer.split())
                    st.caption(get_text('word_count_label', test_lang).format(count=word_count, required=question.get('min_words', 20)))
                    if st.button(get_text('save_answer', test_lang), key=f"save_soft_{i}"):
                        test_system.submit_answer(session_id, q_id, answer)
                        st.success(get_text('answer_saved', test_lang))
                        st.rerun()
            
            elif question['type'] == 'scale':
                # Scale question
                current_answer_dict = session_data.get('answers', {}).get(q_id)
                default_value = int(question['min'])
                # Extract the actual answer value from the dict
                if current_answer_dict and isinstance(current_answer_dict, dict):
                    current_value = int(current_answer_dict.get('answer', default_value))
                else:
                    current_value = default_value
                
                answer = st.slider(
                    get_text('rate_yourself', test_lang) + ":",
                    min_value=int(question['min']),
                    max_value=int(question['max']),
                    value=current_value,
                    key=f"soft_{q_id}"
                )
                
                if answer != current_value:
                    test_system.submit_answer(session_id, q_id, answer)
                    st.rerun()
            
            st.markdown("---")
        
        # No technical questions - only soft skills
        
        # Submission section
        if answered >= total_questions * 0.7:
            st.success(get_text('all_questions_answered', test_lang))
        
        st.markdown("---")
        st.markdown(f"**{get_text('declaration', test_lang)}:**")
        agree = st.checkbox(get_text('declaration_text', test_lang))
        
        if st.button(f"🎯 {get_text('submit_final_assessment', test_lang)}", type="primary", disabled=not agree, width="stretch"):
            if answered < total_questions * 0.7:
                st.error(get_text('answer_70_percent', test_lang))
            else:
                with st.spinner(get_text('submitting_assessment', test_lang)):
                    results = test_system.complete_test(session_id)
                    
                    # Get session data for saving
                    session_data = test_system.test_sessions.get(session_id, {})
                    
                    # Merge personal info from form with candidate data
                    personal_info = st.session_state.get('personal_info', {})
                    candidate_data_to_save = candidate.copy()
                    candidate_data_to_save.update(personal_info)  # Override with form data
                    
                    # Update candidate status
                    candidate['status'] = 'Test Completed'
                    candidate['test_results'] = results
                    candidate['test_submitted_at'] = datetime.now().isoformat()
                    
                    # Update candidate in recruiter.candidates list
                    for idx, c in enumerate(st.session_state.recruiter.candidates):
                        if c.get('id') == cand_id:
                            st.session_state.recruiter.candidates[idx]['status'] = 'Test Completed'
                            st.session_state.recruiter.candidates[idx]['test_results'] = results
                            st.session_state.recruiter.candidates[idx]['test_submitted_at'] = datetime.now().isoformat()
                            break
                    
                    # Save updated candidates to discovered_candidates.json
                    save_discovered_candidates(st.session_state.recruiter.candidates)
                    
                    # SAVE TO FILE - This persists across sessions!
                    save_success = save_test_result(cand_id, candidate_data_to_save, results, session_data)
                    
                    if save_success:
                        st.success(get_text('results_saved', test_lang))
                    else:
                        st.warning(get_text('results_warning', test_lang))
                    
                    # Show thank you message (NO SCORES)
                    st.balloons()
                    st.success(get_text('submission_success', test_lang))
                    
                    st.markdown("---")
                    st.markdown(f"### {get_text('thank_you', test_lang)}")
                    st.info(get_text('next_steps', test_lang))
                    
                    # Clear session
                    if 'personal_info_submitted' in st.session_state:
                        del st.session_state['personal_info_submitted']
    
    # Stop here for candidate view - don't show HR tabs
    st.stop()

# ====================================================================================
# HR VIEW - Show full dashboard with tabs
# ====================================================================================

# Header (will be fixed at top by CSS)
st.title(get_text('app_title', lang))
st.markdown(get_text('app_subtitle', lang))

# Top Navigation Tabs (Sticky)
tab_dashboard, tab_jobs, tab_candidates, tab_tests = st.tabs([
    get_text('tab_dashboard', lang),
    get_text('tab_jobs', lang),
    get_text('tab_candidates', lang),
    get_text('tab_tests', lang)
])

# ==================== TAB 1: HR DASHBOARD ====================
with tab_dashboard:
    st.header(get_text('dashboard_title', lang))
    st.markdown(get_text('dashboard_subtitle', lang))
    
    #  Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_jobs = len(recruiter.job_postings)
    total_candidates = len(recruiter.candidates)
    invited_count = sum(1 for c in recruiter.candidates if c.get('status') == 'Invited')
    completed_count = sum(1 for c in recruiter.candidates if c.get('status') == 'Test Completed')
    
    with col1:
        st.metric(get_text('active_jobs', lang), total_jobs, help=get_text('help_total_candidates', lang))
    with col2:
        st.metric(get_text('total_candidates', lang), total_candidates, help=get_text('help_active_jobs', lang))
    with col3:
        st.metric(get_text('invitations_sent', lang), invited_count, help=get_text('help_invitations', lang))
    with col4:
        st.metric(get_text('tests_completed', lang), completed_count, help=get_text('help_tests_completed', lang))
    
    st.divider()
    
    # Detailed Job Statistics
    st.subheader(get_text('job_statistics', lang))
    
    if recruiter.job_postings:
        for idx, job in enumerate(recruiter.job_postings):
            # Get candidates for this job
            job_candidates = st.session_state.discovered_candidates.get(idx, [])
            
            # Count statuses
            total_for_job = len(job_candidates)
            invited_for_job = sum(1 for cid in job_candidates 
                                 if recruiter.get_candidate_by_id(cid) and 
                                 recruiter.get_candidate_by_id(cid).get('status') == 'Invited')
            completed_for_job = sum(1 for cid in job_candidates 
                                   if recruiter.get_candidate_by_id(cid) and 
                                   recruiter.get_candidate_by_id(cid).get('status') == 'Test Completed')
            pending_for_job = total_for_job - invited_for_job - completed_for_job
            
            with st.expander(f"**{job['title']}** ({total_for_job} {get_text('candidates_found', lang)})", expanded=idx==0):
                # Metrics for this job
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                metric_col1.metric(get_text('total_found', lang), total_for_job)
                metric_col2.metric(get_text('pending', lang), pending_for_job)
                metric_col3.metric(get_text('invited', lang), invited_for_job)
                metric_col4.metric(get_text('completed', lang), completed_for_job)
                
                # Show top candidates if any
                if job_candidates:
                    st.markdown(f"**{get_text('top_candidates', lang)}**")
                    for rank, cid in enumerate(job_candidates[:5], 1):
                        candidate = recruiter.get_candidate_by_id(cid)
                        if candidate:
                            c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
                            c1.write(f"**#{rank}**")
                            c2.write(f"{candidate.get('name')}")
                            c3.write(f"{get_text('status', lang)}: {candidate.get('status', 'Not Invited')}")
                            
                            # Get score if available
                            score_key = (idx, cid)
                            if score_key in st.session_state.candidate_scores:
                                score = st.session_state.candidate_scores[score_key]
                                c4.write(f"⭐ Score: {score.get('total_score', 0):.1f}/100")
                            else:
                                c4.write(get_text('score_pending', lang))
                else:
                    st.info(get_text('no_candidates', lang))
    else:
        st.info(get_text('get_started', lang))
    
    st.divider()
    
    # Recent Activity Timeline
    st.subheader(get_text('recent_activity', lang))
    activities = []
    
    # Collect recent activities
    for candidate in sorted(recruiter.candidates, 
                          key=lambda x: x.get('added_date', '2020-01-01'), 
                          reverse=True)[:10]:
        activities.append({
            "Time": candidate.get('added_date', 'Unknown'),
            "Event": get_text('new_candidate_event', lang).format(name=candidate.get('name')),
            "Type": get_text('discovery_type', lang),
            "Status": candidate.get('status', 'Pending')
        })
    
    if activities:
        st.dataframe(pd.DataFrame(activities), width="stretch", hide_index=True)
    else:
        st.info(get_text('no_recent_activity', lang))

# ==================== TAB 2: JOB POSTINGS ====================
with tab_jobs:
    st.header(get_text('job_postings_management', lang))
    st.markdown(get_text('job_postings_subtitle', lang))
    
    # Sub-tabs for creating and viewing jobs
    subtab_create, subtab_view = st.tabs([get_text('create_new_job', lang), get_text('view_all_jobs', lang)])
    
    with subtab_create:
        st.subheader(get_text('create_job_posting', lang))
        
        with st.form("new_job_form", clear_on_submit=True):
            job_title = st.text_input(get_text('job_title', lang) + " *", placeholder=get_text('job_title_placeholder', lang))
            
            # Combined description input
            st.markdown(get_text('job_description_label', lang))
            job_description_text = st.text_area(
                get_text('paste_or_upload', lang), 
                height=200,
                placeholder=get_text('paste_placeholder', lang),
                label_visibility="collapsed"
            )
            
            uploaded_file = st.file_uploader(
                get_text('upload_or', lang),
                type=['pdf', 'txt', 'md', 'docx', 'doc'],
                help=get_text('supported_formats', lang)
            )
            
            # Process uploaded file if provided
            if uploaded_file:
                try:
                    parser = st.session_state.document_parser
                    file_text = parser.parse_uploaded_file(uploaded_file)
                    job_description_text = file_text  # Override text area with file content
                    st.success(get_text('file_parsed', lang).format(chars=len(file_text)))
                    with st.expander(get_text('preview_text', lang)):
                        st.text(file_text[:500] + "..." if len(file_text) > 500 else file_text)
                except Exception as e:
                    st.error(f"{get_text('error', lang)}: {str(e)}")
            
            submitted = st.form_submit_button(get_text('analyze_save', lang), type="primary", width="stretch")
            
            if submitted:
                if not job_title or not job_description_text:
                    st.error(get_text('provide_title_desc', lang))
                else:
                    with st.spinner(get_text('analyzing_ai', lang)):
                        # Analyze with AI
                        try:
                            requirements = recruiter.parse_job_requirements(job_description_text)
                            
                            # Create job object
                            new_job = {
                                'title': job_title,
                                'description': job_description_text,
                                'created_date': datetime.now().isoformat(),
                                'analysis': requirements
                            }
                            
                            # Store in session state for editing
                            st.session_state['pending_job'] = new_job
                            st.session_state['pending_job_requirements'] = requirements
                            st.success(get_text('job_analyzed', lang))
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"{get_text('error', lang)}: {str(e)}")
        
        # Show analysis results for editing (if job was just analyzed)
        if 'pending_job' in st.session_state:
            st.divider()
            st.subheader(get_text('review_requirements', lang))
            
            job = st.session_state['pending_job']
            requirements = st.session_state['pending_job_requirements']
            
            st.info(get_text('review_info', lang))
            
            # Editable requirements
            st.markdown(f"### {get_text('technical_skills_section', lang)}")
            technical_skills = requirements.get('technical', [])
            
            # Create editable list
            edited_skills = st.text_area(
                get_text('technical_skills_one_per_line', lang),
                value="\n".join(technical_skills),
                height=150,
                help=get_text('edit_skills_help', lang)
            )
            
            # Experience requirements
            col_exp, col_loc = st.columns(2)
            with col_exp:
                experience_years = st.number_input(
                    get_text('years_experience_required', lang),
                    min_value=0,
                    max_value=20,
                    value=requirements.get('experience_years', 3)
                )
            
            with col_loc:
                location = st.text_input(
                    get_text('location_result', lang),
                    value=requirements.get('full_analysis', {}).get('location', 'Remote')
                )
            
            # Priority weights (optional advanced feature)
            st.markdown(f"### {get_text('priority_weights', lang)}")
            with st.expander(get_text('set_custom_weights', lang)):
                st.info(get_text('adjust_weights_info', lang))
                
                col_w1, col_w2, col_w3 = st.columns(3)
                with col_w1:
                    tech_weight = st.slider(get_text('technical_skills_section', lang), 0, 100, 45, key="tech_weight_slider")
                with col_w2:
                    exp_weight = st.slider(get_text('experience', lang), 0, 100, 30, key="exp_weight_slider")
                with col_w3:
                    activity_weight = st.slider(get_text('github_activity', lang), 0, 100, 25, key="activity_weight_slider")
                
                # Calculate normalized weights
                total_weight = tech_weight + exp_weight + activity_weight
                if total_weight > 0:
                    tech_weight_norm = (tech_weight / total_weight) * 100
                    exp_weight_norm = (exp_weight / total_weight) * 100
                    activity_weight_norm = (activity_weight / total_weight) * 100
                    
                    st.markdown(f"**{get_text('normalized_weights', lang)}:**")
                    col_n1, col_n2, col_n3 = st.columns(3)
                    col_n1.metric(get_text('technical_short', lang), f"{tech_weight_norm:.1f}%")
                    col_n2.metric(get_text('experience', lang), f"{exp_weight_norm:.1f}%")
                    col_n3.metric(get_text('activity', lang), f"{activity_weight_norm:.1f}%")
                else:
                    tech_weight_norm = exp_weight_norm = activity_weight_norm = 33.33
            
            # Save buttons
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button(f"💾 {get_text('save_job', lang)}", type="primary", width="stretch"):
                    # Update requirements with edits
                    final_requirements = requirements.copy()
                    final_requirements['technical'] = [s.strip() for s in edited_skills.split('\n') if s.strip()]
                    final_requirements['experience_years'] = experience_years
                    final_requirements['location'] = location
                    
                    # Add custom weights (always normalized to sum to 100)
                    final_requirements['custom_weights'] = {
                        'technical': tech_weight_norm / 100,
                        'experience': exp_weight_norm / 100,
                        'activity': activity_weight_norm / 100
                    }
                    
                    # Update job
                    job['analysis'] = final_requirements
                    job_id = len(recruiter.job_postings)
                    recruiter.job_postings.append(job)
                    st.session_state.job_analysis_cache[job_id] = final_requirements
                    
                    # Save to file for persistence
                    save_job_postings(recruiter.job_postings)
                    
                    # Clear pending job
                    del st.session_state['pending_job']
                    del st.session_state['pending_job_requirements']
                    
                    st.success(get_text('job_saved', lang))
                    time.sleep(1)
                    st.rerun()
            
            with col_cancel:
                if st.button(f"❌ {get_text('cancel', lang)}", width="stretch"):
                    del st.session_state['pending_job']
                    del st.session_state['pending_job_requirements']
                    st.rerun()
    
    with subtab_view:
        st.subheader(get_text('all_job_postings', lang))
        
        if recruiter.job_postings:
            # Display as thumbnails/cards
            for idx, job in enumerate(recruiter.job_postings):
                # Get candidate count
                candidate_count = len(st.session_state.discovered_candidates.get(idx, []))
                
                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <h3>{job['title']}</h3>
                        <p><strong>{get_text('company', lang)}:</strong> {job.get('company', 'N/A')}</p>
                        <p><strong>{get_text('candidates_found_label', lang)}:</strong> {candidate_count}</p>
                        <p><strong>{get_text('created', lang)}:</strong> {job.get('created_date', 'N/A')[:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col_view, col_edit, col_delete = st.columns([2, 2, 1])
                    
                    with col_view:
                        if st.button(f"👁️ {get_text('view_details_btn', lang)}", key=f"view_{idx}", width="stretch"):
                            st.session_state[f'show_details_{idx}'] = not st.session_state.get(f'show_details_{idx}', False)
                    
                    with col_edit:
                        if st.button(f"✏️ {get_text('edit_requirements', lang)}", key=f"edit_{idx}", width="stretch"):
                            st.session_state['editing_job_id'] = idx
                    
                    with col_delete:
                        if st.button(f"🗑️", key=f"delete_{idx}", help=get_text('delete_job', lang)):
                            recruiter.job_postings.pop(idx)
                            if idx in st.session_state.discovered_candidates:
                                del st.session_state.discovered_candidates[idx]
                            st.success(get_text('job_deleted', lang))
                            st.rerun()
                    
                    # Show details if requested
                    if st.session_state.get(f'show_details_{idx}', False):
                        with st.expander(get_text('job_details', lang), expanded=True):
                            st.markdown(f"**{get_text('description', lang)}:**")
                            st.write(job['description'][:500] + "..." if len(job['description']) > 500 else job['description'])
                            
                            if 'analysis' in job:
                                st.markdown(f"**{get_text('requirements', lang)}:**")
                                st.write(f"**{get_text('technical_skills_section', lang)}:** {', '.join(job['analysis'].get('technical', []))}")
                                st.write(f"**{get_text('experience', lang)}:** {job['analysis'].get('experience_years', 'N/A')} {get_text('years', lang)}")
                                st.write(f"**{get_text('location_result', lang)}:** {job['analysis'].get('location', 'N/A')}")
                    
                    st.divider()
            
            # Edit modal (if editing)
            if 'editing_job_id' in st.session_state:
                edit_idx = st.session_state['editing_job_id']
                job_to_edit = recruiter.job_postings[edit_idx]
                
                st.subheader(f"✏️ {get_text('edit_requirements_for', lang)}: {job_to_edit['title']}")
                
                current_analysis = job_to_edit.get('analysis', {})
                
                new_skills = st.text_area(
                    get_text('technical_skills_section', lang),
                    value="\n".join(current_analysis.get('technical', [])),
                    height=150
                )
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_exp = st.number_input(
                        get_text('years_experience_required', lang),
                        value=current_analysis.get('experience_years', 3)
                    )
                with col_e2:
                    new_loc = st.text_input(
                        get_text('location_result', lang),
                        value=current_analysis.get('location', '')
                    )
                
                col_save_edit, col_cancel_edit = st.columns(2)
                with col_save_edit:
                    if st.button(f"💾 {get_text('save', lang)}", type="primary"):
                        current_analysis['technical'] = [s.strip() for s in new_skills.split('\n') if s.strip()]
                        current_analysis['experience_years'] = new_exp
                        current_analysis['location'] = new_loc
                        job_to_edit['analysis'] = current_analysis
                        del st.session_state['editing_job_id']
                        st.success(get_text('success', lang))
                        st.rerun()
                
                with col_cancel_edit:
                    if st.button(get_text('cancel', lang)):
                        del st.session_state['editing_job_id']
                        st.rerun()
        else:
            st.info(get_text('no_jobs', lang))

# ==================== TAB 3: CANDIDATE DISCOVERY ====================
with tab_candidates:
    # Import and render the candidate discovery tab
    from modules.candidate_discovery_tab import render_candidate_discovery_tab
    render_candidate_discovery_tab(recruiter, lang)

# ==================== TAB 4: CANDIDATE TESTS ====================
with tab_tests:
    st.header(get_text('test_results_review', lang))
    
    st.markdown(f"### {get_text('hr_view_results', lang)}")
    
    # Info box explaining how candidates access tests
    with st.expander(get_text('how_testing_works', lang), expanded=False):
        st.markdown("""
        **Candidate Testing Flow:**
        
        1. Go to **Candidate Discovery** tab
        2. Run discovery to fetch real candidates from GitHub
        3. Click **Generate Invitation** on any candidate
        4. **Copy the test link** (e.g., `http://localhost:<your_port>?cid=<id>`) and share
        5. Candidate completes assessment
        6. Review results here in the Tests tab
        
        **Test a link yourself:**
        """)
        example_port = st.get_option("server.port") or 8501
        st.code(f"http://localhost:{example_port}?cid=1", language=None)
        st.caption("Open in new tab/incognito to see candidate view")
    
    # Load test results from file (persistent storage)
    file_results = load_test_results()
    
    # Also get any in-memory results
    memory_candidates = [c for c in recruiter.candidates if c.get('status') == 'Test Completed']
    
    # Combine results (prefer file results as they're more recent)
    all_results = file_results.copy()
    
    # Add memory-only results if not in file
    file_ids = {r.get('candidate_id') for r in file_results}
    for c in memory_candidates:
        if c.get('id') not in file_ids:
            all_results.append(c)
    
    if not all_results:
        st.info(get_text('no_completed_tests', lang))
        st.caption(get_text('test_results_tip', lang))
    else:
        st.success(f"📊 {len(all_results)} {get_text('candidates_completed', lang)}")
        st.caption(f"💾 {len(file_results)} {get_text('saved_to_file', lang)} | {len(memory_candidates)} {get_text('in_memory', lang)}")
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            job_filter = st.selectbox(
                get_text('filter_by_job', lang) + ":",
                [get_text('all_jobs', lang)] + [job['title'] for job in recruiter.job_postings] if recruiter.job_postings else [get_text('all_jobs', lang)]
            )
        with col_filter2:
            sort_by = st.selectbox(
                get_text('sort_by', lang),
                [get_text('submission_date_newest', lang), get_text('submission_date_oldest', lang), 
                 get_text('name_a_z', lang), get_text('name_z_a', lang)]
            )
        
        # Apply filters
        filtered_candidates = all_results.copy()
        
        # Sort - use the translation keys instead of hardcoded strings
        if sort_by == get_text('submission_date_newest', lang):
            filtered_candidates.sort(key=lambda x: x.get('test_submitted_at', ''), reverse=True)
        elif sort_by == get_text('submission_date_oldest', lang):
            filtered_candidates.sort(key=lambda x: x.get('test_submitted_at', ''))
        elif sort_by == get_text('name_a_z', lang):
            filtered_candidates.sort(key=lambda x: x.get('name', ''))
        else:  # Name (Z-A)
            filtered_candidates.sort(key=lambda x: x.get('name', ''), reverse=True)
        
        # Display test results
        st.markdown("---")
        
        for idx, candidate in enumerate(filtered_candidates):
            with st.expander(f"👤 {candidate.get('name', 'Unknown')} - Test Results", expanded=False):
                test_results = candidate.get('test_results', {})
                
                # Candidate Info
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.markdown(f"**📧 {get_text('email_label', lang)}:** {candidate.get('email', 'N/A')}")
                    st.markdown(f"**📱 {get_text('phone_label', lang)}:** {candidate.get('phone', 'N/A')}")
                with col_info2:
                    st.markdown(f"**💼 {get_text('linkedin_label', lang)}:** {candidate.get('linkedin', 'N/A')}")
                    st.markdown(f"**📍 {get_text('location_result', lang)}:** {candidate.get('location', 'N/A')}")
                with col_info3:
                    submitted_at = candidate.get('test_submitted_at', 'N/A')
                    if submitted_at != 'N/A':
                        from datetime import datetime
                        dt = datetime.fromisoformat(submitted_at)
                        submitted_at = dt.strftime("%Y-%m-%d %H:%M")
                    st.markdown(f"**📅 {get_text('submitted_label', lang)}:** {submitted_at}")
                    st.markdown(f"**⏱️ {get_text('time_taken_label', lang)}:** {test_results.get('time_taken_minutes', 0):.1f} {get_text('min_short', lang)}")
                
                st.markdown("---")
                
                # Mock Scores (placeholder for future LLM scoring)
                st.markdown(f"### {get_text('assessment_scores', lang)}")
                col_score1, col_score2, col_score3, col_score4 = st.columns(4)
                with col_score1:
                    st.metric(get_text('overall_score', lang), f"{test_results.get('overall_score', 75):.0f}/100", 
                             help="Mock score - will be replaced with LLM evaluation")
                with col_score2:
                    st.metric(get_text('soft_skill_score', lang), f"{test_results.get('soft_skill_score', 78):.0f}/100")
                with col_score3:
                    st.metric(get_text('technical_score', lang), f"{test_results.get('technical_score', 72):.0f}/100")
                with col_score4:
                    cheating_flags = test_results.get('cheating_flags', 0)
                    st.metric(f"🚩 {get_text('flags_label', lang)}", cheating_flags, delta=f"-{test_results.get('cheating_penalty', 0):.0f}%")
                
                # Strengths & Weaknesses
                col_sw1, col_sw2 = st.columns(2)
                with col_sw1:
                    st.markdown(f"**{get_text('strengths', lang)}**")
                    for strength in test_results.get('strengths', [get_text('completed_assessment', lang)]):
                        st.markdown(f"- {strength}")
                with col_sw2:
                    st.markdown(f"**{get_text('weaknesses', lang)}**")
                    for weakness in test_results.get('weaknesses', [get_text('none_identified', lang)]):
                        st.markdown(f"- {weakness}")
                
                st.markdown("---")
                
                # Questions & Answers
                st.markdown(f"### {get_text('detailed_responses', lang)}")
                
                # Try to get session data from memory or from saved data
                session_id = test_results.get('session_id')
                session_data = None
                
                if session_id and session_id in test_system.test_sessions:
                    # Get from memory (active session)
                    session_data = test_system.test_sessions[session_id]
                elif 'session_data' in candidate:
                    # Get from file (saved session)
                    session_data = candidate.get('session_data')
                
                if session_data:
                    # Soft Skill Questions
                    st.markdown(f"#### {get_text('soft_skills_assessment', lang)}")
                    for i, question in enumerate(session_data.get('soft_skill_questions', []), 1):
                        q_id = question['id']
                        answer_data = session_data.get('answers', {}).get(q_id, {})
                        
                        st.markdown(f"**Q{i}: {question['question']}**")
                        
                        if question['type'] == 'multiple_choice':
                            answer_idx = answer_data.get('answer') if isinstance(answer_data, dict) else None
                            if answer_idx is not None:
                                st.info(f"✓ {question['options'][answer_idx]}")
                            else:
                                st.warning(get_text('no_answer_provided', lang))
                        elif question['type'] == 'text':
                            answer_text = answer_data.get('answer', '') if isinstance(answer_data, dict) else ''
                            if answer_text:
                                st.text_area(f"{get_text('answer', lang)}:", answer_text, height=100, disabled=True, key=f"soft_{idx}_{q_id}_view")
                                st.caption(f"{get_text('word_count', lang)}: {len(answer_text.split())} {get_text('words', lang)}")
                            else:
                                st.warning(get_text('no_answer_provided', lang))
                        elif question['type'] == 'scale':
                            answer_val = answer_data.get('answer') if isinstance(answer_data, dict) else None
                            if answer_val is not None:
                                st.info(f"{get_text('rating', lang)}: {answer_val}/{question['max']}")
                            else:
                                st.warning(get_text('no_answer_provided', lang))
                        
                        st.markdown("")
                    
                    # Technical Questions
                    st.markdown(f"#### {get_text('technical_assessment', lang)}")
                    for i, question in enumerate(session_data.get('technical_questions', []), 1):
                        q_id = question['id']
                        answer_data = session_data.get('answers', {}).get(q_id, {})
                        
                        st.markdown(f"**Q{i}: {question['question']}**")
                        
                        if question['type'] == 'text':
                            answer_text = answer_data.get('answer', '') if isinstance(answer_data, dict) else ''
                            if answer_text:
                                st.text_area(f"{get_text('answer', lang)}:", answer_text, height=120, disabled=True, key=f"tech_{idx}_{q_id}_view")
                                st.caption(f"{get_text('word_count', lang)}: {len(answer_text.split())} {get_text('words', lang)}")
                            else:
                                st.warning(get_text('no_answer_provided', lang))
                        elif question['type'] == 'scale':
                            answer_val = answer_data.get('answer') if isinstance(answer_data, dict) else None
                            if answer_val is not None:
                                st.info(f"{get_text('rating', lang)}: {answer_val}/{question['max']}")
                            else:
                                st.warning(get_text('no_answer_provided', lang))
                        
                        st.markdown("")
                else:
                    st.warning(get_text('session_data_unavailable', lang))
                
                # Action buttons
                st.markdown("---")
                col_action1, col_action2, col_action3 = st.columns(3)
                with col_action1:
                    if st.button(f"✉️ {get_text('contact_candidate', lang)}", key=f"contact_{idx}"):
                        st.info(f"{get_text('email_label', lang)}: {candidate.get('email', 'N/A')}")
                with col_action2:
                    if st.button(f"📊 {get_text('export_results', lang)}", key=f"export_tests_{idx}"):
                        st.info(get_text('export_coming_soon', lang))
                with col_action3:
                    if st.button(f"🗑️ {get_text('delete_results', lang)}", key=f"delete_tests_{idx}"):
                        st.warning(get_text('delete_coming_soon', lang))

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: #666; padding: 2rem;'>"
    "<strong>TalentSonar Team</strong> - Smart Recruiting Platform"
    "</div>",
    unsafe_allow_html=True
)
