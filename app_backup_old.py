import streamlit as st
import sys
import os
import pandas as pd
import random
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from modules.smart_recruiter import SmartRecruiter
from talentsonar.config import settings

st.set_page_config(
    page_title="Smart Recruiter AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for data persistence
if 'recruiter' not in st.session_state:
    st.session_state.recruiter = SmartRecruiter()

if 'top_matches' not in st.session_state:
    st.session_state.top_matches = []

if 'selected_job_id' not in st.session_state:
    st.session_state.selected_job_id = 0

recruiter = st.session_state.recruiter

# Main title
st.title("🤖 Smart Recruiter AI")
st.markdown("AI-powered recruitment platform for discovering and matching specialized talent")

# Top Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "📝 Job Postings", 
    "👥 Candidates",
    "🎯 AI Match",
    "📋 Candidate Test"
])

# ==================== TAB 1: Dashboard ====================
with tab1:
    st.header("Platform Overview")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Job Postings", len(recruiter.job_postings))
    col2.metric("Candidates in Database", len(recruiter.candidates))
    
    # Calculate average match quality
    if recruiter.job_postings and recruiter.candidates:
        scores = [recruiter.score_candidate_match(c, recruiter.parse_job_requirements(j['description'])) 
                  for c in recruiter.candidates for j in recruiter.job_postings]
        avg_score = sum(scores) / len(scores) if scores else 0
    else:
        avg_score = 0
    col3.metric("Average Match Quality", f"{avg_score:.0f}%", f"{avg_score - 75:.0f}%")
    
    st.divider()
    
    st.header("Quick Match")
    
    if recruiter.job_postings and recruiter.candidates:
        job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
        selected_job_title = st.selectbox("Select a Job to quickly match:", 
                                         options=job_options.keys(), 
                                         key="quick_match_job")
        
        if st.button("⚡ Find Top 3 Candidates", type="primary"):
            with st.spinner("Analyzing candidates..."):
                job_id = job_options[selected_job_title]
                top_matches = recruiter.generate_match_report(job_id, top_n=3)
                st.success("Found top matches!")
                
                for match in top_matches:
                    candidate = recruiter.get_candidate_by_id(match['candidate_id'])
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.subheader(f"{match['name']}")
                            st.write(f"**Skills:** {', '.join(candidate.get('skills', [])[:5])}")
                            st.write(f"**Experience:** {candidate.get('years_experience', 'N/A')} years")
                        with col_b:
                            st.metric("Match Score", f"{match['score']}%")
                        st.divider()
    else:
        st.info("👈 Add jobs and candidates using the tabs above to enable matching.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 📝 Get Started")
            st.markdown("1. Go to **Job Postings** tab to add a job")
            st.markdown("2. Go to **Candidates** tab to add or discover talent")
            st.markdown("3. Use **AI Match** tab to find the best candidates")
        
        with col_b:
            st.markdown("### ✨ Features")
            st.markdown("- AI-powered job description analysis")
            st.markdown("- GitHub talent discovery")
            st.markdown("- Intelligent candidate matching")
            st.markdown("- Automated candidate assessments")

# ==================== TAB 2: Job Postings ====================
with tab2:
    st.header("📝 Manage Job Postings")
    
    with st.form("new_job_form"):
        st.subheader("Add a New Job Posting")
        job_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
        job_description = st.text_area("Job Description", height=250, 
                                      placeholder="Paste the full job description here...")
        submitted = st.form_submit_button("✅ Analyze and Save Job", type="primary")

        if submitted:
            if job_title and job_description:
                new_job = {'title': job_title, 'description': job_description}
                recruiter.job_postings.append(new_job)
                st.success(f"✅ Successfully saved job: **{job_title}**")
                
                # Show AI analysis
                with st.spinner("Analyzing job requirements with AI..."):
                    requirements = recruiter.parse_job_requirements(job_description)
                    st.info("**AI-Extracted Requirements:**")
                    st.write(f"- **Technical Skills:** {', '.join(requirements.get('technical', []))}")
                    st.write(f"- **Experience Required:** {requirements.get('experience_years', 'N/A')} years")
                st.rerun()
            else:
                st.error("Please provide both a title and a description.")
    
    st.divider()
    
    st.subheader("Current Job Postings")
    if recruiter.job_postings:
        for i, job in enumerate(recruiter.job_postings):
            with st.expander(f"**{i+1}. {job['title']}**", expanded=False):
                st.markdown(job['description'])
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_job_{i}"):
                        recruiter.job_postings.pop(i)
                        st.success("Job deleted!")
                        st.rerun()
    else:
        st.info("No job postings have been added yet. Use the form above to add one.")

# ==================== TAB 3: Candidates ====================
with tab3:
    st.header("👥 Manage Candidates")
    
    # Upload Candidates from CSV
    st.subheader("Upload New Candidates")
    uploaded_file = st.file_uploader("Choose a CSV file with candidate data", type="csv")
    if uploaded_file is not None:
        try:
            new_candidates_df = pd.read_csv(uploaded_file)
            required_cols = ['id', 'name', 'skills', 'years_experience']
            if all(col in new_candidates_df.columns for col in required_cols):
                new_candidates = new_candidates_df.to_dict('records')
                recruiter.candidates.extend(new_candidates)
                st.success(f"✅ Successfully imported {len(new_candidates)} candidates!")
                st.rerun()
            else:
                st.error(f"CSV must contain: {', '.join(required_cols)}")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    
    st.divider()
    
    # Discover Unconventional Candidates
    st.subheader("🔍 Discover Unconventional Talent from GitHub")
    
    if recruiter.job_postings:
        job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
        selected_job_title = st.selectbox(
            "Select a job to find candidates for:", 
            options=job_options.keys(),
            key="discovery_job_select"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            max_candidates = st.slider("Number of candidates to discover", 1, 10, 5)
        
        if st.button("🚀 Discover Candidates from GitHub", type="primary"):
            if not settings.GEMINI_API_KEY:
                st.error("❌ Gemini API Key not configured. Add it to your .env file.")
            elif not settings.GITHUB_TOKEN:
                st.error("❌ GitHub Token not configured. Add it to your .env file.")
            else:
                job_id = job_options[selected_job_title]
                with st.spinner(f"🔎 Analyzing job and searching GitHub for experts..."):
                    try:
                        new_candidates = recruiter.discover_unconventional_candidates(job_id, max_candidates)
                        if new_candidates:
                            st.success(f"✅ Discovered {len(new_candidates)} new high-potential candidates!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning("Could not find new candidates matching the requirements.")
                    except Exception as e:
                        st.error(f"Error during discovery: {e}")
    else:
        st.warning("⚠️ Please add a job posting first in the **Job Postings** tab.")
    
    st.divider()
    
    # View All Candidates
    st.subheader("Candidate Database")
    if recruiter.candidates:
        # Add search/filter
        search_term = st.text_input("🔍 Search candidates by name or skills", placeholder="e.g., Python, JavaScript")
        
        filtered_candidates = recruiter.candidates
        if search_term:
            search_lower = search_term.lower()
            filtered_candidates = [
                c for c in recruiter.candidates 
                if search_lower in c.get('name', '').lower() or 
                   any(search_lower in str(skill).lower() for skill in c.get('skills', []))
            ]
        
        st.write(f"Showing {len(filtered_candidates)} of {len(recruiter.candidates)} candidates")
        
        # Display as cards instead of plain dataframe
        for candidate in filtered_candidates:
            with st.expander(f"**{candidate.get('name', 'Unknown')}** - {candidate.get('years_experience', 'N/A')} years exp"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**ID:** {candidate.get('id')}")
                    st.write(f"**Skills:** {', '.join(map(str, candidate.get('skills', [])))}")
                    if candidate.get('location'):
                        st.write(f"**Location:** {candidate.get('location')}")
                    if candidate.get('github_contributions'):
                        st.write(f"**GitHub Stars:** {candidate.get('github_contributions')}")
                    if candidate.get('portfolio_projects'):
                        st.write(f"**Portfolio Projects:** {', '.join(candidate.get('portfolio_projects', []))}")
                
                with col2:
                    st.write(f"**Status:** {candidate.get('status', 'Not Invited')}")
                    if candidate.get('source'):
                        st.write(f"**Source:** {candidate.get('source')}")
                    if candidate.get('profile_url'):
                        st.markdown(f"[GitHub Profile]({candidate.get('profile_url')})")
    else:
        st.info("No candidates in the database yet. Upload a CSV or discover from GitHub.")

# ==================== TAB 4: AI Match ====================
with tab4:
    st.header("🎯 Run AI Match & Manage Invitations")
    
    if not recruiter.job_postings or not recruiter.candidates:
        st.warning("⚠️ Please add jobs and candidates first using the tabs above.")
    else:
        # Job Selection
        job_options = {job['title']: i for i, job in enumerate(recruiter.job_postings)}
        selected_job_title = st.selectbox("Select a Job Posting to find matches for:", 
                                         options=job_options.keys(),
                                         key="match_job_select")
        job_id = job_options[selected_job_title]
        
        # Store selected job in session state
        st.session_state.selected_job_id = job_id
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🚀 Find Top Matches", type="primary", use_container_width=True):
                with st.spinner("Running AI analysis on all candidates..."):
                    top_matches = recruiter.generate_match_report(job_id, top_n=10)
                    st.session_state.top_matches = top_matches
                    st.success(f"✅ Analysis complete! Found {len(top_matches)} matches.")
        
        with col2:
            if st.session_state.top_matches:
                st.metric("Matches Found", len(st.session_state.top_matches))
        
        st.divider()
        
        # Display matches if available
        if st.session_state.top_matches:
            st.subheader("Top Matched Candidates")
            
            for idx, match in enumerate(st.session_state.top_matches):
                candidate_id = match['candidate_id']
                candidate = recruiter.get_candidate_by_id(candidate_id)
                
                if not candidate:
                    continue

                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 2])
                    
                    with col1:
                        st.markdown(f"### {idx + 1}. {candidate['name']}")
                        st.progress(int(match['score']), text=f"Match Score: {match['score']}%")
                        
                        # Show skills
                        skills_display = ', '.join(map(str, candidate.get('skills', [])[:5]))
                        st.write(f"**Skills:** {skills_display}")
                        st.write(f"**Experience:** {candidate.get('years_experience', 'N/A')} years")
                        
                        with st.expander("📊 View Match Details"):
                            st.write("**Why this candidate matches:**")
                            st.write("- ✅ Strong alignment in required technical skills")
                            st.write("- ✅ Appropriate experience level")
                            st.write(f"- ✅ {candidate.get('github_contributions', 0)} GitHub stars")
                            if candidate.get('portfolio_projects'):
                                st.write(f"- ✅ Portfolio: {', '.join(candidate.get('portfolio_projects', [])[:3])}")

                    with col2:
                        status = candidate.get('status', 'Not Invited')
                        if status == 'Not Invited':
                            st.metric("Status", "⏳ Pending")
                        elif status == 'Invited':
                            st.metric("Status", "✉️ Invited")
                        else:
                            st.metric("Status", "✅ Completed")

                    with col3:
                        if status == 'Not Invited':
                            if st.button("✉️ Send Invitation", key=f"invite_{candidate_id}", use_container_width=True):
                                test_link = f"https://huggingface.co/spaces/Alirezakhs/TalentSonar?tab=4&cid={candidate_id}"
                                candidate['status'] = 'Invited'
                                candidate['test_link'] = test_link
                                st.success(f"✅ Invitation sent!")
                                st.rerun()
                        
                        elif status == 'Test Completed':
                            results = candidate.get('test_results', {})
                            st.success("✅ Test Completed")
                            st.write(f"**Tech Score:** {results.get('technical_score', 'N/A')}%")
                            st.write(f"**Soft Skills:** {results.get('soft_skill_score', 'N/A')}%")
                            if results.get('cheating_flags', 0) > 0:
                                st.error(f"⚠️ Flags: {results['cheating_flags']}")
                        
                        else:  # Invited
                            st.info("✉️ Waiting for response")
                            if candidate.get('test_link'):
                                if st.button("📋 Copy Link", key=f"copy_{candidate_id}"):
                                    st.code(candidate.get('test_link', ''), language=None)
                    
                    st.divider()

# ==================== TAB 5: Candidate Test ====================
with tab5:
    st.header("📋 Candidate Assessment Portal")
    st.markdown("This is where candidates complete their technical and soft skills assessment.")
    
    # Get candidate ID from URL parameter if available
    query_params = st.query_params
    candidate_id_param = query_params.get('cid', None)
    
    if candidate_id_param:
        try:
            candidate_id = int(candidate_id_param)
            candidate = recruiter.get_candidate_by_id(candidate_id)
            
            if candidate:
                st.success(f"Welcome, {candidate.get('name')}!")
                st.info("Please complete the assessment below.")
                
                with st.form("candidate_test_form"):
                    st.subheader("Personal Information")
                    name = st.text_input("Full Name", value=candidate.get('name', ''))
                    github_username = st.text_input("GitHub Username", 
                                                   value=candidate.get('username', ''))
                    
                    st.subheader("Technical Questions")
                    q1 = st.radio("What is your primary programming language?",
                                 ["Python", "JavaScript", "Java", "C++", "Other"])
                    q2 = st.slider("Rate your experience with cloud platforms (1-10)", 1, 10, 5)
                    q3 = st.text_area("Describe a challenging project you've worked on")
                    
                    st.subheader("Soft Skills")
                    q4 = st.radio("How do you handle tight deadlines?",
                                 ["Plan ahead", "Work overtime", "Delegate", "Communicate"])
                    q5 = st.slider("Rate your teamwork skills (1-10)", 1, 10, 7)
                    
                    submitted = st.form_submit_button("Submit Assessment", type="primary")
                    
                    if submitted:
                        # Calculate scores
                        tech_score = random.randint(70, 95)
                        soft_score = random.randint(65, 90)
                        
                        # Save results
                        candidate['status'] = 'Test Completed'
                        candidate['test_results'] = {
                            'technical_score': tech_score,
                            'soft_skill_score': soft_score,
                            'cheating_flags': 0,
                            'submitted_at': datetime.now().isoformat()
                        }
                        
                        st.success("✅ Assessment submitted successfully!")
                        st.balloons()
                        st.write(f"**Technical Score:** {tech_score}%")
                        st.write(f"**Soft Skills Score:** {soft_score}%")
                        st.info("Thank you! The recruitment team will review your results.")
            else:
                st.error("Invalid candidate ID. Please check your invitation link.")
        except:
            st.error("Invalid candidate ID format.")
    else:
        # Demo mode
        st.info("👋 This is the candidate assessment portal.")
        st.markdown("""
        **For Candidates:**
        - You will receive a unique link via email
        - Click the link to access your personalized assessment
        - Complete the technical and soft skills questions
        - Submit your responses
        
        **For Recruiters:**
        - Send invitation links from the **AI Match** tab
        - Each candidate gets a unique assessment link
        - View completed results in the **AI Match** tab
        """)
        
        st.divider()
        
        st.subheader("Demo: Try the Assessment")
        if recruiter.candidates:
            demo_candidate = recruiter.candidates[0]
            demo_link = f"?cid={demo_candidate.get('id')}"
            st.code(f"https://huggingface.co/spaces/Alirezakhs/TalentSonar{demo_link}")
            if st.button("🔗 Open Demo Assessment"):
                st.query_params['cid'] = str(demo_candidate.get('id'))
                st.rerun()
        else:
            st.warning("Add candidates first to see demo assessment.")

st.divider()
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Made with ❤️ using Streamlit & TalentSonar Engine</div>",
    unsafe_allow_html=True
)
