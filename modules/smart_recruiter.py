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
        self.scraper = GitHubScraper(api_token=settings.GITHUB_TOKEN)
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
            # Convert the Pydantic model to a dict and extract relevant info
            analysis_dict = analysis_result.model_dump()
            return {
                'technical': [skill['requirement'] for skill in analysis_dict.get('technical_skills', [])],
                'experience_years': analysis_dict.get('experience', [{}])[0].get('years_experience', 3)
            }
        except Exception as e:
            print(f"Error during job analysis: {e}. Falling back to mock data.")
            return {'technical': ['react', 'typescript'], 'experience_years': 3}
    
    def score_candidate_match(self, candidate, job_requirements):
        """(REAL) Calculate matching score using the TalentSonar TalentMatcher."""
        try:
            # The matcher expects a specific structure, we adapt our data to it.
            score = self.matcher.calculate_match_score(candidate, job_requirements)
            return score
        except Exception as e:
            print(f"Error during matching: {e}. Falling back to mock scoring.")
            return self._mock_score(candidate, job_requirements)

    def discover_unconventional_candidates(self, job_id, max_candidates=5):
        """(REAL) Discover candidates from GitHub based on a job's requirements."""
        if not self.scraper.api_token:
            raise ValueError("GitHub token not found. Please add it to your .env file.")
        
        # 1. Get the job and its required skills
        job = self.job_postings[job_id]
        requirements = self.parse_job_requirements(job['description'])
        
        # 2. Build a smart search query
        # Example: "language:python language:django"
        query = " ".join([f"language:{skill.lower()}" for skill in requirements.get('technical', [])[:2]])
        if not query:
            raise ValueError("Could not generate a search query from job requirements.")

        # 3. Scrape GitHub
        discovered_users = self.scraper.search_users_by_skill(query, limit=max_candidates)
        
        # 4. Convert the scraper's output into our app's candidate format
        new_candidates = []
        for user in discovered_users:
            new_id = len(self.candidates) + len(new_candidates) + 1
            candidate = {
                'id': new_id,
                'name': user.get('login', 'N/A'),
                'skills': requirements.get('technical', []), # Assume they have the skills we searched for
                'years_experience': random.randint(1, 5),
                'github_contributions': user.get('contributions', 0),
                'portfolio_projects': [],
                'recent_certifications': 0,
                'status': 'Not Invited',
                'source': 'GitHub Discovery'
            }
            new_candidates.append(candidate)
        
        self.candidates.extend(new_candidates)
        return new_candidates

    def _mock_score(self, candidate, job_requirements):
        """A fallback scoring method."""
        tech_match = len(set(candidate.get('skills', [])) & set(job_requirements.get('technical', [])))
        return min(tech_match * 25, 100)

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
