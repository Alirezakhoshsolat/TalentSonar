import random
from datetime import datetime
import os
from dotenv import load_dotenv

# --- Integration with TalentSonar ---
# Add the project root to the Python path to find the 'talentsonar' module
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from talentsonar.src.job_analyzer import JobAnalyzer
from talentsonar.src.github_scraper import GitHubScraper
from talentsonar.src.talent_matcher import TalentMatcher
from talentsonar.config import settings

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
        self.load_initial_data()

    def load_initial_data(self):
        # Pre-load some mock jobs and candidates to start with
        self.job_postings = [
            {'title': 'Senior Python Developer', 'description': 'A job for a Python expert with 5+ years of experience in Django and AWS.'},
            {'title': 'Frontend React Engineer', 'description': 'Requires strong skills in React, TypeScript, and 3+ years experience.'}
        ]
        self.candidates = [
            {
                'id': 1, 'name': 'Alice Johnson', 'skills': ['Python', 'Django', 'AWS', 'PostgreSQL'], 
                'years_experience': 5, 'github_contributions': 150, 'portfolio_projects': ['E-commerce Backend', 'Data Pipeline', 'Internal Tool'], 
                'recent_certifications': 1, 'status': 'Not Invited'
            }
        ]

    def get_candidate_by_id(self, candidate_id):
        for candidate in self.candidates:
            if candidate['id'] == candidate_id:
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
        """(REAL) Discover candidates from GitHub based on a job's requirements."""
        if not self.scraper.github_token:
            raise ValueError("GitHub token not found. Please add GITHUB_TOKEN to your .env file.")
        
        # 1. Get the job and analyze it
        job = self.job_postings[job_id]
        requirements = self.parse_job_requirements(job['description'])
        
        # 2. Build a smart GitHub search query (similar to talent_pipeline.py logic)
        query_parts = []
        tech_skills = requirements.get('technical', [])
        
        # Add language filters for top skills
        lang_map = {
            "python": "python", "javascript": "javascript", "java": "java",
            "typescript": "typescript", "go": "go", "rust": "rust",
            "ruby": "ruby", "php": "php", "c++": "cpp", "c#": "csharp",
            "react": "javascript", "vue": "javascript", "angular": "javascript",
            "django": "python", "flask": "python", "node": "javascript"
        }
        
        for skill in tech_skills[:3]:  # Top 3 skills
            skill_lower = skill.lower()
            for name, gh_lang in lang_map.items():
                if name in skill_lower and f"language:{gh_lang}" not in query_parts:
                    query_parts.append(f"language:{gh_lang}")
                    break
        
        # Add quality filters
        query_parts.append("followers:>=10")
        query_parts.append("repos:>=5")
        
        query = " ".join(query_parts)
        if not query:
            raise ValueError("Could not generate a search query from job requirements.")

        # 3. Search GitHub for users
        print(f"Searching GitHub with query: {query}")
        search_results = self.scraper.search_users(query, max_results=max_candidates)
        
        if not search_results:
            return []
        
        # 4. Analyze each candidate's GitHub profile
        new_candidates = []
        for user in search_results:
            username = user.get('username')
            print(f"Analyzing GitHub user: @{username}")
            
            # Get full candidate analysis
            analysis = self.scraper.analyze_candidate_skills(username)
            
            if "error" in analysis:
                continue
            
            # Extract info for our candidate format
            profile = analysis.get('profile', {})
            stats = analysis.get('statistics', {})
            languages = list(analysis.get('languages', {}).keys())[:5]
            
            new_id = len(self.candidates) + len(new_candidates) + 1
            candidate = {
                'id': new_id,
                'name': profile.get('name') or username,
                'username': username,
                'skills': languages + analysis.get('technologies', [])[:5],
                'years_experience': random.randint(2, 8),  # Could calculate from account age
                'github_contributions': stats.get('total_stars', 0),
                'portfolio_projects': [repo['name'] for repo in analysis.get('repositories', [])[:3]],
                'recent_certifications': 0,
                'status': 'Not Invited',
                'source': 'GitHub Discovery',
                'profile_url': profile.get('profile_url', ''),
                'location': profile.get('location'),
                'github_analysis': analysis  # Store full analysis for potential matching
            }
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
