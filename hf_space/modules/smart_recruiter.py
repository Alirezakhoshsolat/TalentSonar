import random
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio

# --- Integration with TalentSonar ---
# Add the project root to the Python path to find the 'talentsonar' module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from talentsonar.src.job_analyzer import JobAnalyzer
from talentsonar.src.github_scraper import GitHubScraper
from talentsonar.src.talent_matcher import TalentMatcher
from talentsonar.config import settings
from modules.github_discovery import discover_candidates_for_job

# Load environment variables from .env file
load_dotenv()

# --- Configure TalentSonar Settings ---
# This is critical for the engine to work.
settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
settings.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class SmartRecruiter:
    """
    An integrated AI-powered candidate matching system using the TalentSonar engine.
    """
    
    def __init__(self):
        # Initialize the real tools from TalentSonar
        self.job_analyzer = JobAnalyzer(api_key=settings.GEMINI_API_KEY)
        self.scraper = GitHubScraper(github_token=settings.GITHUB_TOKEN)
        self.matcher = TalentMatcher()
        
        self.candidates = []
        self.job_postings = []
        
        # Cache for GitHub profiles to reduce API calls
        self.github_profile_cache = {}
        
        self.load_initial_data()

    def load_initial_data(self):
        # Start clean; no mock jobs or candidates. Jobs and candidates will be loaded from files by app.py if present.
        self.job_postings = []
        self.candidates = []

    def get_candidate_by_id(self, candidate_id):
        # Handle both int and string IDs
        try:
            cid = int(candidate_id)
        except (ValueError, TypeError):
            return None
            
        for candidate in self.candidates:
            if int(candidate.get('id', -1)) == cid:
                return candidate
        return None

    def parse_job_requirements(self, job_description):
        """(REAL) Extract skills from a job posting using the TalentSonar JobAnalyzer."""
        if not self.job_analyzer.api_key:
            print("Warning: GEMINI_API_KEY not found. Using mock analysis.")
            return {'technical': ['python', 'django'], 'experience_years': 5}
            
        try:
            analysis_result = self.job_analyzer.analyze_job_description(job_description)
            # Convert the Pydantic model to a dict
            analysis_dict = analysis_result.model_dump()
            
            # Extract years from experience array
            exp_years = 3  # default
            experience_list = analysis_dict.get('experience', [])
            if experience_list and len(experience_list) > 0:
                exp_years = experience_list[0].get('years_experience', 3) or 3
            
            return {
                'technical': [skill['requirement'] for skill in analysis_dict.get('technical_skills', [])],
                'experience_years': exp_years,
                'full_analysis': analysis_dict  # Keep full analysis for matching
            }
        except Exception as e:
            print(f"Error during job analysis: {e}. Falling back to mock data.")
            return {'technical': ['react', 'typescript'], 'experience_years': 3}
    
    def score_candidate_match(self, candidate, job_requirements):
        """Calculate matching score - uses simplified algorithm for UI candidates."""
        # For candidates that came from GitHub discovery, they have full analysis data
        # For manually added candidates, we use simple scoring
        return self._mock_score(candidate, job_requirements)

    def discover_unconventional_candidates(self, job_id, max_candidates=5):
        """(REAL) Discover candidates using GitHub GraphQL and scoring (no mocks)."""
        if not self.scraper.github_token:
            raise ValueError("GitHub token not found. Please add GITHUB_TOKEN to your .env file.")

        # 1. Get the job and analyze it (prefer precomputed analysis to avoid slow LLM calls)
        job = self.job_postings[job_id]
        requirements = job.get('analysis') or self.parse_job_requirements(job['description'])
        tech_skills = requirements.get('technical', [])

        # 2. Run GraphQL-based discovery and scoring
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Running inside an event loop (e.g., Streamlit experimental), create task and run with asyncio.run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    discover_candidates_for_job(tech_skills, max_candidates=max_candidates, github_token=self.scraper.github_token),
                    loop,
                )
                gh_candidates = future.result()
            else:
                gh_candidates = asyncio.run(
                    discover_candidates_for_job(tech_skills, max_candidates=max_candidates, github_token=self.scraper.github_token)
                )
        except Exception as e:
            print(f"GraphQL discovery failed: {e}")
            gh_candidates = []

        # 3. If nothing found, fallback to REST-based discovery via TalentSonar
        if not gh_candidates:
            print("GraphQL returned no candidates; falling back to REST search/analysis")
            # Build a simple query from top technical skills
            lang_map = {
                "python": "python", "javascript": "javascript", "java": "java",
                "typescript": "typescript", "go": "go", "rust": "rust",
                "ruby": "ruby", "php": "php", "c++": "cpp", "c#": "csharp",
                "react": "javascript", "vue": "javascript", "angular": "javascript",
                "django": "python", "flask": "python", "node": "javascript"
            }
            query_parts = []
            for skill in tech_skills[:3]:
                s = skill.lower()
                for key, gh_lang in lang_map.items():
                    if key in s and f"language:{gh_lang}" not in query_parts:
                        query_parts.append(f"language:{gh_lang}")
                        break
            query_parts += ["followers:>=10", "repos:>=5"]
            query = " ".join(query_parts) if query_parts else "repos:>=5 followers:>=10"

            users = self.scraper.search_users(query, max_results=max_candidates)
            if not users:
                # Try unauthenticated as a last resort (limited to 60 req/hr)
                alt_scraper = GitHubScraper(github_token=None)
                users = alt_scraper.search_users(query, max_results=max_candidates)
            new_candidates = []
            for user in users or []:
                username = user.get('username') or user.get('login')
                if not username:
                    continue
                # Use cache if available
                if username in self.github_profile_cache:
                    analysis = self.github_profile_cache[username]
                else:
                    # Use whichever scraper generated the users list
                    scraper_used = self.scraper if users and users is not None else alt_scraper
                    analysis = scraper_used.analyze_candidate_skills(username)
                    if "error" in analysis:
                        continue
                    self.github_profile_cache[username] = analysis
                profile = analysis.get('profile', {})
                stats = analysis.get('statistics', {})
                languages = list(analysis.get('languages', {}).keys())[:5]
                new_id = len(self.candidates) + len(new_candidates) + 1
                candidate = {
                    'id': new_id,
                    'name': profile.get('name') or username,
                    'username': username,
                    'skills': languages + analysis.get('technologies', [])[:5],
                    'years_experience': random.randint(2, 8),
                    'github_contributions': stats.get('total_stars', 0),
                    'portfolio_projects': [repo['name'] for repo in analysis.get('repositories', [])[:3]],
                    'recent_certifications': 0,
                    'status': 'Not Invited',
                    'source': 'GitHub Discovery (REST fallback)',
                    'profile_url': profile.get('profile_url', ''),
                    'location': profile.get('location'),
                    'github_analysis': analysis
                }
                # Provide an immediate match_score using a lightweight heuristic
                try:
                    candidate['match_score'] = self._mock_score(candidate, requirements)
                except Exception:
                    candidate['match_score'] = 0.0
                new_candidates.append(candidate)
            self.candidates.extend(new_candidates)
            return new_candidates

        # 4. Map GraphQL results to our candidate schema
        new_candidates = []
        for item in gh_candidates:
            username = item.get('login') or ''
            new_id = len(self.candidates) + len(new_candidates) + 1
            skills = list(dict.fromkeys((item.get('langsFound', []) + item.get('topicsFound', []))))[:10]
            portfolio_projects = [r.get('name') for r in item.get('portfolio', []) if r.get('name')][:3]

            candidate = {
                'id': new_id,
                'name': item.get('name') or username,
                'username': username,
                'skills': skills,
                'years_experience': random.randint(2, 8),
                'github_contributions': item.get('total_stars', 0),
                'portfolio_projects': portfolio_projects,
                'recent_certifications': 0,
                'status': 'Not Invited',
                'source': 'GitHub Discovery (GraphQL)',
                'profile_url': f"https://github.com/{username}" if username else '',
                'location': item.get('location') or '',
                'discovery_score': item.get('score', 0.0),
                'discovery_reasons': item.get('reasons', []),
                'github_graphql': item,
            }
            # Bridge for UI sorting/meters
            candidate['match_score'] = candidate['discovery_score']
            new_candidates.append(candidate)

        self.candidates.extend(new_candidates)
        return new_candidates

    def _mock_score(self, candidate, job_requirements):
        """A simplified scoring method for UI candidates."""
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        required_skills = set([s.lower() for s in job_requirements.get('technical', [])])
        
        if not required_skills:
            return 50.0
        
        # Calculate overlap
        matched = candidate_skills & required_skills
        match_ratio = len(matched) / len(required_skills)
        
        # Base score from skill match (0-70 points)
        score = match_ratio * 70
        
        # Bonus for experience match (0-20 points)
        required_years = job_requirements.get('experience_years', 3)
        candidate_years = candidate.get('years_experience', 0)
        if candidate_years >= required_years:
            score += 20
        elif candidate_years >= required_years * 0.7:
            score += 10
        
        # Bonus for GitHub activity (0-10 points)
        if candidate.get('github_contributions', 0) > 100:
            score += 10
        elif candidate.get('github_contributions', 0) > 50:
            score += 5
        
        return min(round(score, 2), 100.0)

    def generate_match_report(self, job_id, top_n=10):
        """Generate ranked candidate list for a job posting"""
        job = self.job_postings[job_id]
        requirements = self.parse_job_requirements(job['description'])
        
        scores = [
            {
                'candidate_id': c['id'],
                'name': c['name'],
                'score': self.score_candidate_match(c, requirements),
                'timestamp': datetime.now().isoformat()
            }
            for c in self.candidates
        ]
        
        return sorted(scores, key=lambda x: x['score'], reverse=True)[:top_n]
    
    def clear_github_cache(self):
        """Clear the GitHub profile cache to force fresh data."""
        self.github_profile_cache.clear()
        print("GitHub profile cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics."""
        return {
            'cached_profiles': len(self.github_profile_cache),
            'usernames': list(self.github_profile_cache.keys())
        }
