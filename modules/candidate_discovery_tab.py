"""
Candidate Discovery Tab Module
Handles the candidate discovery interface for TalentSonar
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from talentsonar.src.talent_matcher import TalentMatcher
from modules.github_discovery import map_technical_to_languages
from modules.translations import get_text
import os
import json
from typing import List, Dict, Any


# Helper function to save discovered candidates
def save_discovered_candidates_to_file(candidates):
    """Save discovered candidates to JSON file."""
    try:
        discovered_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'discovered_candidates.json')
        os.makedirs(os.path.dirname(discovered_file), exist_ok=True)
        with open(discovered_file, 'w') as f:
            json.dump(candidates, f, indent=2)
    except Exception as e:
        st.error(f"Error saving candidates: {e}")


# Helper function to persist invitations (for tracking/testing later)
def save_invitation_record(invitation: Dict[str, Any]):
    """Append or update an invitation record in data/invitations.json."""
    try:
        invitations_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'invitations.json')
        os.makedirs(os.path.dirname(invitations_file), exist_ok=True)

        existing: List[Dict[str, Any]] = []
        if os.path.exists(invitations_file):
            with open(invitations_file, 'r', encoding='utf-8') as f:
                try:
                    existing = json.load(f) or []
                except json.JSONDecodeError:
                    existing = []

        # Upsert by candidate_id
        updated = False
        for i, rec in enumerate(existing):
            if rec.get('candidate_id') == invitation.get('candidate_id'):
                existing[i] = invitation
                updated = True
                break
        if not updated:
            existing.append(invitation)

        with open(invitations_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving invitation: {e}")


def render_candidate_discovery_tab(recruiter, lang='en'):
    """Render the candidate discovery tab content."""
    st.header(get_text('discovery_title', lang))
    st.markdown(get_text('discovery_subtitle', lang))
    
    if not recruiter.job_postings:
        st.warning(get_text('create_job_first', lang))
        return
    
    # Job selection
    st.subheader(get_text('select_job_section', lang))
    job_options = {f"{job['title']} ({job.get('company', 'N/A')})": idx 
                   for idx, job in enumerate(recruiter.job_postings)}
    selected_job_name = st.selectbox(
        get_text('choose_job', lang),
        options=list(job_options.keys()),
        key="discovery_job_select"
    )
    selected_job_id = job_options[selected_job_name]
    st.session_state.selected_job_id = selected_job_id
    
    # Show job requirements
    selected_job = recruiter.job_postings[selected_job_id]
    with st.expander(get_text('view_job_requirements', lang)):
        if 'analysis' in selected_job:
            analysis = selected_job['analysis']
            st.write(f"**{get_text('required_skills', lang)}:** {', '.join(analysis.get('technical', []))}")
            st.write(f"**{get_text('experience', lang)}:** {analysis.get('experience_years', 'N/A')} {get_text('years', lang)}")
            st.write(f"**{get_text('location', lang)}:** {analysis.get('location', 'Remote')}")
    
    st.divider()
    
    # Discovery section
    st.subheader(get_text('run_discovery', lang))
    # (Intentionally minimal UI; internal mappings are handled under the hood)
    
    # Show cache info for GitHub mode only (mock removed)
    cache_stats = recruiter.get_cache_stats()
    if cache_stats['cached_profiles'] > 0:
        col_cache1, col_cache2 = st.columns([3, 1])
        with col_cache1:
            st.caption(f"💾 {cache_stats['cached_profiles']} GitHub profiles cached (reduces API calls)")
        with col_cache2:
            if st.button(get_text('clear_cache', lang), help="Clear cached profiles to fetch fresh data"):
                recruiter.clear_github_cache()
                st.success(get_text('cache_cleared', lang))
                st.rerun()
    
    col_disc1, col_disc2 = st.columns([3, 1])
    
    with col_disc1:
        max_candidates = st.number_input(
            get_text('num_candidates_discover', lang),
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help=get_text('num_candidates_help', lang)
        )
    
    with col_disc2:
        st.metric(get_text('current_candidates', lang), 
                 len(st.session_state.discovered_candidates.get(selected_job_id, [])))
    
    if st.button(get_text('discover_button', lang), type="primary", width="stretch"):
        # GITHUB API MODE - Check rate limits
        rate_limit_info = recruiter.scraper.get_rate_limit_status()
        
        if rate_limit_info:
            core_limit = rate_limit_info.get('resources', {}).get('core', {})
            remaining = core_limit.get('remaining', 0)
            limit = core_limit.get('limit', 60)
            reset_timestamp = core_limit.get('reset', 0)
            
            if reset_timestamp:
                reset_time = datetime.fromtimestamp(reset_timestamp)
                time_until_reset = reset_time - datetime.now()
                minutes_until_reset = int(time_until_reset.total_seconds() / 60)
            else:
                minutes_until_reset = 0
            
            # Show rate limit status
            st.info(f"📊 **GitHub API Status:** {remaining}/{limit} requests remaining")
            
            if remaining < 10:
                st.error(f"⚠️ **Rate Limit Critical!** Only {remaining} requests left. Resets in {minutes_until_reset} minutes.")
                st.warning("**Solutions:**")
                st.markdown("""
                1. **Switch to Mock Data Mode** above (recommended for testing)
                2. **Wait** for rate limit to reset
                3. **Add GitHub Token** to .env file for 5000 requests/hour:
                   - Create token at: https://github.com/settings/tokens
                   - Add to `.env`: `GITHUB_TOKEN=your_token_here`
                4. **Reduce** number of candidates to discover
                """)
                if remaining == 0:
                    st.stop()
        
        if not recruiter.scraper.github_token:
            st.warning("⚠️ No GitHub token configured - limited to 60 requests/hour.")
            st.info("💡 Add GITHUB_TOKEN to .env file for 5000 requests/hour!")
        
        if not recruiter.job_analyzer.api_key:
            st.error("❌ Gemini API key not configured. Please add GEMINI_API_KEY to your .env file.")
        else:
            with st.spinner(f"🔍 Searching GitHub and analyzing profiles... This may take a few minutes."):
                try:
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Analyzing job requirements...")
                    progress_bar.progress(10)
                    
                    # Show cache stats
                    cache_stats = recruiter.get_cache_stats()
                    if cache_stats['cached_profiles'] > 0:
                        st.info(f"💾 Using {cache_stats['cached_profiles']} cached profiles to reduce API calls")
                    
                    # Discover candidates
                    new_candidates = recruiter.discover_unconventional_candidates(selected_job_id, max_candidates)
                    progress_bar.progress(70)
                    
                    if new_candidates:
                        status_text.text("Calculating match scores...")
                        
                        # Add job_id to all new candidates
                        for candidate in new_candidates:
                            candidate['job_id'] = selected_job_id
                        
                        # Calculate detailed scores using TalentMatcher
                        matcher = TalentMatcher()
                        job_analysis = selected_job.get('analysis', {})
                        
                        # Convert our analysis format to TalentMatcher format
                        job_analysis_for_matcher = {
                            'technical_skills': [
                                {'requirement': skill, 'importance': 'required'}
                                for skill in job_analysis.get('technical', [])
                            ],
                            'experience': [
                                {'years_experience': job_analysis.get('experience_years', 3)}
                            ]
                        }
                        
                        for candidate in new_candidates:
                            cid = candidate['id']
                            
                            # If we have full GitHub analysis, use TalentMatcher
                            if 'github_analysis' in candidate:
                                try:
                                    score_obj = matcher.match_candidate(
                                        candidate['github_analysis'],
                                        job_analysis_for_matcher
                                    )
                                    
                                    # Store detailed scores
                                    score_key = (selected_job_id, cid)
                                    st.session_state.candidate_scores[score_key] = {
                                        'total_score': score_obj.total_score,
                                        'technical_skills_score': score_obj.technical_skills_score,
                                        'experience_score': score_obj.experience_score,
                                        'activity_score': score_obj.activity_score,
                                        'education_score': score_obj.education_score,
                                        'soft_skills_score': score_obj.soft_skills_score,
                                        'matched_skills': score_obj.matched_skills,
                                        'missing_skills': score_obj.missing_skills,
                                        'bonus_skills': score_obj.bonus_skills
                                    }
                                    
                                    # Update candidate with score
                                    candidate['match_score'] = score_obj.total_score
                                    
                                except Exception as e:
                                    st.warning(f"Could not calculate detailed score for {candidate['name']}: {str(e)}")
                        
                        progress_bar.progress(100)
                        
                        # Store discovered candidates for this job
                        existing = st.session_state.discovered_candidates.get(selected_job_id, [])
                        new_ids = [c['id'] for c in new_candidates]
                        st.session_state.discovered_candidates[selected_job_id] = existing + new_ids
                        
                        # Save all discovered candidates to file
                        save_discovered_candidates_to_file(recruiter.candidates)
                        
                        st.success(f"✅ Discovered {len(new_candidates)} new candidates!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("No candidates found matching the requirements.")
                        
                except ValueError as e:
                    error_msg = str(e)
                    if "GitHub token" in error_msg:
                        st.error("❌ GitHub API Error: Token not configured")
                        st.markdown("""
                        **How to fix:**
                        1. Create a GitHub Personal Access Token at: https://github.com/settings/tokens
                        2. Add it to your `.env` file: `GITHUB_TOKEN=your_token_here`
                        3. Restart the application
                        """)
                    elif "rate limit" in error_msg.lower():
                        st.error("❌ GitHub Rate Limit Exceeded")
                        st.markdown("""
                        **Solutions:**
                        - Wait for the rate limit to reset (shown above)
                        - Add a GitHub token for 5000 requests/hour
                        - Reduce number of candidates to discover
                        - Clear cache and try again later
                        """)
                    else:
                        st.error(f"Error: {error_msg}")
                        
                except Exception as e:
                    st.error(f"⚠️ Unexpected error during discovery: {str(e)}")
                    with st.expander("Show error details"):
                        import traceback
                        st.code(traceback.format_exc())
    
    st.divider()
    
    # Show discovered candidates
    st.subheader(get_text('discovered_dataset', lang))
    
    job_candidate_ids = st.session_state.discovered_candidates.get(selected_job_id, [])
    
    if job_candidate_ids:
        # Get full candidate objects
        job_candidates = [recruiter.get_candidate_by_id(cid) for cid in job_candidate_ids]
        job_candidates = [c for c in job_candidates if c is not None]
        
        # Sort by score
        job_candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Filter and extraction
        col_filter, col_extract = st.columns([3, 1])
        
        with col_filter:
            min_score_filter = st.slider(
                get_text('min_match_score', lang),
                0, 100, 0,
                help=get_text('min_match_score_help', lang)
            )
        
        with col_extract:
            top_n = st.number_input(get_text('extract_top_n', lang), 1, len(job_candidates), min(5, len(job_candidates)))
        
        # Filter candidates
        filtered_candidates = [c for c in job_candidates if c.get('match_score', 0) >= min_score_filter]
        
        st.write(get_text('showing_candidates', lang).format(filtered=len(filtered_candidates), total=len(job_candidates)))
        
        # Display candidates in detail
        for rank, candidate in enumerate(filtered_candidates, 1):
            cid = candidate['id']
            score_key = (selected_job_id, cid)
            detailed_scores = st.session_state.candidate_scores.get(score_key, {})
            
            with st.expander(
                f"**#{rank} - {candidate.get('name')}** | Overall: {candidate.get('match_score', 0):.1f}/100",
                expanded=(rank <= 3)
            ):
                # Main info
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.markdown(f"**{get_text('basic_info', lang)}**")
                    st.write(f"{get_text('full_name', lang)}: {candidate.get('name')}")
                    st.write(f"{get_text('github_username', lang)}: @{candidate.get('username', 'N/A')}")
                    st.write(f"{get_text('location_result', lang)}: {candidate.get('location', 'N/A')}")
                    if candidate.get('profile_url'):
                        st.markdown(f"[{get_text('github_profile', lang)}]({candidate['profile_url']})")
                
                with col_info2:
                    st.markdown(f"**{get_text('experience_section', lang)}**")
                    st.write(f"{get_text('years_label', lang)}: {candidate.get('years_experience', 'N/A')}")
                    st.write(f"{get_text('github_stars', lang)}: {candidate.get('github_contributions', 0)}")
                    st.write(f"{get_text('status', lang)}: {candidate.get('status', get_text('not_invited', lang))}")
                
                with col_info3:
                    st.markdown(f"**{get_text('match_score_section', lang)}**")
                    overall_score = candidate.get('match_score', 0)
                    st.progress(int(overall_score), text=f"{overall_score:.1f}/100")
                
                # Skills section
                st.markdown(f"**{get_text('skills_technologies', lang)}**")
                skills = candidate.get('skills', [])
                if skills:
                    st.write(", ".join(map(str, skills[:10])))
                
                # Portfolio
                if candidate.get('portfolio_projects'):
                    st.markdown(f"**{get_text('portfolio_projects', lang)}**")
                    st.write(", ".join(candidate['portfolio_projects'][:5]))
                
                # Detailed scoring breakdown
                if detailed_scores:
                    st.markdown(f"**{get_text('detailed_score_breakdown', lang)}**")
                    
                    score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns(5)
                    score_col1.metric(get_text('technical_short', lang), f"{detailed_scores.get('technical_skills_score', 0):.0f}")
                    score_col2.metric(get_text('experience', lang), f"{detailed_scores.get('experience_score', 0):.0f}")
                    score_col3.metric(get_text('activity', lang), f"{detailed_scores.get('activity_score', 0):.0f}")
                    score_col4.metric(get_text('education', lang), f"{detailed_scores.get('education_score', 0):.0f}")
                    score_col5.metric(get_text('soft_skills', lang), f"{detailed_scores.get('soft_skills_score', 0):.0f}")
                    
                    # Matched/Missing skills
                    matched_col, missing_col = st.columns(2)
                    
                    with matched_col:
                        matched_skills = detailed_scores.get('matched_skills', [])
                        if matched_skills:
                            st.success(get_text('matched_skills_label', lang).format(count=len(matched_skills)))
                            st.write(", ".join(matched_skills[:10]))
                    
                    with missing_col:
                        missing_skills = detailed_scores.get('missing_skills', [])
                        if missing_skills:
                            st.warning(get_text('missing_skills_label', lang).format(count=len(missing_skills)))
                            st.write(", ".join(missing_skills[:5]))
                    
                    # Bonus skills
                    bonus_skills = detailed_scores.get('bonus_skills', [])
                    if bonus_skills:
                        st.info(get_text('bonus_skills_label', lang).format(skills=', '.join(bonus_skills[:8])))
                
                # Action buttons
                if candidate.get('status') != 'Invited':
                    if st.button(f"📧 {get_text('generate_invitation', lang)}", key=f"gen_invite_{cid}", width="stretch"):
                        # Generate unique credentials
                        username = f"candidate_{cid}"
                        import random
                        import string
                        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                        # Build link dynamically based on current Streamlit server port
                        port = st.get_option("server.port") or 8501
                        base_url = f"http://localhost:{port}"
                        # app.py handles candidate view at root when 'cid' is present
                        test_link = f"{base_url}?cid={cid}"
                        
                        # Update candidate with credentials
                        candidate['status'] = 'Invited'
                        candidate['invited_date'] = datetime.now().isoformat()
                        candidate['test_link'] = test_link
                        candidate['username'] = username
                        candidate['password'] = password
                        
                        # IMPORTANT: Update in recruiter.candidates list too
                        for idx, c in enumerate(st.session_state.recruiter.candidates):
                            if c.get('id') == cid:
                                st.session_state.recruiter.candidates[idx] = candidate
                                break
                        
                        # Save candidates to file after generating invitation
                        save_discovered_candidates_to_file(st.session_state.recruiter.candidates)
                        
                        # Compose and persist invitation
                        invitation_record = {
                            'candidate_id': cid,
                            'name': candidate['name'],
                            'link': test_link,
                            'username': username,
                            'password': password,
                            'invited_date': candidate['invited_date']
                        }
                        st.session_state[f'invitation_{cid}'] = {
                            'link': test_link,
                            'username': username,
                            'password': password,
                            'name': candidate['name']
                        }

                        # Build the full invitation text using translations
                        invitation_text = (
                            f"{get_text('dear', lang)} {candidate['name']},\n\n"
                            f"{get_text('invitation_body', lang).format(test_link=test_link, username=username, password=password)}"
                        )

                        invitation_record['invitation_text'] = invitation_text

                        # Save to invitations.json for later testing/traceability
                        save_invitation_record(invitation_record)
                        
                        st.rerun()
                else:
                    # Show generated invitation
                    invitation = st.session_state.get(f'invitation_{cid}', {})
                    if invitation:
                        st.success(get_text('invitation_generated', lang))

                        invitation_text = (
                            f"{get_text('dear', lang)} {invitation['name']},\n\n"
                            f"{get_text('invitation_body', lang).format(test_link=invitation['link'], username=invitation['username'], password=invitation['password'])}"
                        )

                        st.text_area(get_text('invitation_details', lang), invitation_text, height=250, key=f"inv_text_{cid}")

                        if st.button(get_text('copy_invitation', lang), key=f"copy_inv_{cid}", width="stretch"):
                            st.write("")  # Placeholder - copy functionality
                            st.info(f"💡 {get_text('invitation_copied', lang)} (In production, this would use clipboard API)")
                            st.code(invitation_text, language=None)
    else:
        st.info(get_text('no_candidates_yet', lang))
