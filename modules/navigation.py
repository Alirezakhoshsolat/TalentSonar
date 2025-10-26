"""
Shared navigation component for all pages
"""
import streamlit as st


def render_top_navigation():
    """Render a top navigation bar with tabs for all pages"""
    
    # Custom CSS for top navigation
    st.markdown("""
        <style>
        .nav-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 2rem;
            background-color: white;
            border-radius: 0.5rem 0.5rem 0 0;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ff4b4b;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for navigation
    tabs = st.tabs([
        "🏠 Dashboard",
        "📝 Job Postings", 
        "👥 Candidates",
        "🎯 AI Match",
        "📋 Candidate Test"
    ])
    
    return tabs


def init_session_state():
    """Initialize all session state variables for data persistence"""
    from modules.smart_recruiter import SmartRecruiter
    
    # Initialize the recruiter engine if not exists
    if 'recruiter' not in st.session_state:
        st.session_state.recruiter = SmartRecruiter()
    
    # Initialize other persistent state variables
    if 'top_matches' not in st.session_state:
        st.session_state.top_matches = []
    
    if 'selected_job_id' not in st.session_state:
        st.session_state.selected_job_id = None
    
    if 'last_analysis_timestamp' not in st.session_state:
        st.session_state.last_analysis_timestamp = None


def get_recruiter():
    """Get the recruiter instance from session state"""
    if 'recruiter' not in st.session_state:
        init_session_state()
    return st.session_state.recruiter


def save_state(key, value):
    """Save a value to session state"""
    st.session_state[key] = value


def get_state(key, default=None):
    """Get a value from session state with optional default"""
    return st.session_state.get(key, default)
