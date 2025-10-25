"""
Talent Matching Engine

Matches GitHub candidates against job requirements and scores their fit.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CandidateScore(BaseModel):
    """Model for candidate scoring results."""
    username: str
    total_score: float = Field(..., description="Overall match score (0-100)")
    
    # Component scores
    technical_skills_score: float = Field(0.0, description="Technical skills match (0-100)")
    experience_score: float = Field(0.0, description="Experience level score (0-100)")
    activity_score: float = Field(0.0, description="GitHub activity score (0-100)")
    education_score: float = Field(0.0, description="Education match score (0-100)")
    soft_skills_score: float = Field(0.0, description="Soft skills indicators (0-100)")
    
    # Detailed breakdown
    matched_skills: List[str] = Field(default_factory=list, description="Skills that match requirements")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills not found")
    bonus_skills: List[str] = Field(default_factory=list, description="Extra valuable skills")
    
    # Candidate info
    profile_url: str = ""
    location: Optional[str] = None
    hireable: Optional[bool] = None
    
    # Metadata
    match_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TalentMatcher:
    """
    Engine for matching GitHub candidates against job requirements.
    """
    
    def __init__(self):
        """Initialize the talent matcher."""
        self.logger = self._setup_logging()
        
        # Skill weight mappings
        self.skill_weights = {
            "required": 1.0,
            "preferred": 0.6,
            "nice_to_have": 0.3
        }
        
        # Score component weights (must sum to 1.0)
        self.component_weights = {
            "technical_skills": 0.45,
            "experience": 0.20,
            "activity": 0.15,
            "education": 0.10,
            "soft_skills": 0.10
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the matcher."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _normalize_skill_name(self, skill: str) -> str:
        """
        Normalize skill names for matching.
        
        Args:
            skill (str): Skill name
            
        Returns:
            Normalized skill name
        """
        # Convert to lowercase, remove special chars
        normalized = skill.lower().strip()
        
        # Common synonyms
        synonyms = {
            "javascript": ["js", "javascript", "ecmascript"],
            "typescript": ["ts", "typescript"],
            "python": ["python", "py"],
            "react": ["react", "reactjs", "react.js"],
            "node": ["node", "nodejs", "node.js"],
            "vue": ["vue", "vuejs", "vue.js"],
            "angular": ["angular", "angularjs"],
            "postgresql": ["postgres", "postgresql", "psql"],
            "mongodb": ["mongo", "mongodb"],
            "kubernetes": ["k8s", "kubernetes"],
            "docker": ["docker", "containerization"],
            "aws": ["aws", "amazon web services"],
            "machine learning": ["ml", "machine learning", "machinelearning"],
            "artificial intelligence": ["ai", "artificial intelligence"],
        }
        
        # Check if skill matches any synonym group
        for canonical, variants in synonyms.items():
            if normalized in variants or any(variant in normalized for variant in variants):
                return canonical
        
        return normalized
    
    def _extract_required_skills(self, job_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract required skills from job analysis by importance level.
        
        Args:
            job_analysis (dict): Job analysis result from JobAnalyzer
            
        Returns:
            Dictionary of skill lists by importance
        """
        skills_by_importance = {
            "required": [],
            "preferred": [],
            "nice_to_have": []
        }
        
        # Extract from technical skills
        for skill in job_analysis.get("technical_skills", []):
            skill_name = self._normalize_skill_name(skill["requirement"])
            importance = skill["importance"]
            if importance in skills_by_importance:
                skills_by_importance[importance].append(skill_name)
        
        # Extract from certifications
        for cert in job_analysis.get("certifications", []):
            cert_name = self._normalize_skill_name(cert["requirement"])
            importance = cert["importance"]
            if importance in skills_by_importance:
                skills_by_importance[importance].append(cert_name)
        
        return skills_by_importance
    
    def _calculate_technical_skills_score(
        self,
        candidate_analysis: Dict[str, Any],
        required_skills: Dict[str, List[str]]
    ) -> tuple[float, List[str], List[str], List[str]]:
        """
        Calculate technical skills match score.
        
        Args:
            candidate_analysis (dict): Candidate GitHub analysis
            required_skills (dict): Required skills by importance
            
        Returns:
            Tuple of (score, matched_skills, missing_skills, bonus_skills)
        """
        # Extract candidate skills
        candidate_skills = set()
        
        # From languages
        for lang in candidate_analysis.get("languages", {}).keys():
            candidate_skills.add(self._normalize_skill_name(lang))
        
        # From technologies
        for tech in candidate_analysis.get("technologies", []):
            candidate_skills.add(self._normalize_skill_name(tech))
        
        # From repository topics
        for repo in candidate_analysis.get("repositories", []):
            for topic in repo.get("topics", []):
                candidate_skills.add(self._normalize_skill_name(topic))
        
        matched_skills = []
        missing_skills = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Check each requirement level
        for importance, skills in required_skills.items():
            weight = self.skill_weights[importance]
            
            for skill in skills:
                normalized_skill = self._normalize_skill_name(skill)
                total_weight += weight
                
                # Check for match (exact or partial)
                is_match = False
                for candidate_skill in candidate_skills:
                    if (normalized_skill in candidate_skill or 
                        candidate_skill in normalized_skill or
                        normalized_skill == candidate_skill):
                        is_match = True
                        break
                
                if is_match:
                    matched_skills.append(skill)
                    total_weighted_score += weight
                else:
                    if importance == "required":
                        missing_skills.append(skill)
        
        # Calculate score (0-100)
        score = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0
        
        # Identify bonus skills (candidate has but not required)
        all_required = set(
            self._normalize_skill_name(s) 
            for skills in required_skills.values() 
            for s in skills
        )
        bonus_skills = [
            skill for skill in candidate_skills 
            if skill not in all_required and skill not in ["", " "]
        ]
        
        return score, matched_skills, missing_skills, bonus_skills[:10]  # Top 10 bonus skills
    
    def _calculate_experience_score(
        self,
        candidate_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate experience level score based on GitHub activity history.
        
        Args:
            candidate_analysis (dict): Candidate GitHub analysis
            job_analysis (dict): Job requirements
            
        Returns:
            Experience score (0-100)
        """
        score = 0.0
        
        # Check account age (proxy for years of experience)
        profile = candidate_analysis.get("profile", {})
        created_at = profile.get("created_at")
        
        if created_at:
            # Parse the datetime and make it timezone-aware
            created_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now_datetime = datetime.now(timezone.utc)
            
            account_age_years = (now_datetime - created_datetime).days / 365.25
            
            # Extract required years from job
            required_years = 0
            for exp in job_analysis.get("experience", []):
                years = exp.get("years_experience", 0)
                if years and years > required_years:
                    required_years = years
            
            # Score based on account age vs required experience
            if required_years > 0:
                age_ratio = min(account_age_years / required_years, 1.5)
                score += min(age_ratio * 40, 50)  # Max 50 points
            else:
                score += min(account_age_years * 10, 50)  # 10 points per year, max 50
        
        # Repository count and quality
        stats = candidate_analysis.get("statistics", {})
        original_repos = stats.get("original_repos", 0)
        score += min(original_repos * 2, 30)  # 2 points per original repo, max 30
        
        # Stars received (indication of code quality)
        total_stars = stats.get("total_stars", 0)
        score += min(total_stars * 0.5, 20)  # 0.5 points per star, max 20
        
        return min(score, 100)
    
    def _calculate_activity_score(self, candidate_analysis: Dict[str, Any]) -> float:
        """
        Calculate GitHub activity score (recent contributions, consistency).
        
        Args:
            candidate_analysis (dict): Candidate GitHub analysis
            
        Returns:
            Activity score (0-100)
        """
        score = 0.0
        
        # Check recency of latest activity
        latest_activity = candidate_analysis.get("latest_activity")
        if latest_activity:
            # Parse the datetime and make it timezone-aware
            activity_datetime = datetime.fromisoformat(latest_activity.replace("Z", "+00:00"))
            now_datetime = datetime.now(timezone.utc)
            
            days_since_activity = (now_datetime - activity_datetime).days
            
            # Recent activity scores higher
            if days_since_activity < 7:
                score += 40
            elif days_since_activity < 30:
                score += 30
            elif days_since_activity < 90:
                score += 20
            elif days_since_activity < 180:
                score += 10
        
        # Number of repositories
        stats = candidate_analysis.get("statistics", {})
        total_repos = stats.get("total_repos", 0)
        score += min(total_repos * 1.5, 30)  # Max 30 points
        
        # Community engagement (followers)
        followers = stats.get("followers", 0)
        score += min(followers * 0.5, 20)  # Max 20 points
        
        # Contribution quality (forks of their repos)
        total_forks = stats.get("total_forks", 0)
        score += min(total_forks * 0.3, 10)  # Max 10 points
        
        return min(score, 100)
    
    def _calculate_education_score(
        self,
        candidate_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate education match score based on profile information.
        
        Args:
            candidate_analysis (dict): Candidate GitHub analysis
            job_analysis (dict): Job requirements
            
        Returns:
            Education score (0-100)
        """
        # GitHub doesn't have direct education info, so we infer from:
        # - Bio keywords
        # - Company (if from educational institution)
        # - Overall code quality indicators
        
        score = 50.0  # Base score (neutral)
        
        profile = candidate_analysis.get("profile", {})
        bio = (profile.get("bio") or "").lower()
        company = (profile.get("company") or "").lower()
        
        # Check for education keywords in bio
        education_keywords = [
            "phd", "doctorate", "master", "bachelor", "university", 
            "college", "student", "graduate", "cs", "computer science",
            "engineering", "mathematics", "statistics"
        ]
        
        matches = sum(1 for keyword in education_keywords if keyword in bio or keyword in company)
        score += min(matches * 10, 30)  # Up to 30 bonus points
        
        # High-quality contributions can compensate for formal education
        stats = candidate_analysis.get("statistics", {})
        if stats.get("total_stars", 0) > 100:
            score += 20
        
        return min(score, 100)
    
    def _calculate_soft_skills_score(
        self,
        candidate_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate soft skills score based on GitHub activity indicators.
        
        Args:
            candidate_analysis (dict): Candidate GitHub analysis
            job_analysis (dict): Job requirements
            
        Returns:
            Soft skills score (0-100)
        """
        score = 0.0
        
        profile = candidate_analysis.get("profile", {})
        stats = candidate_analysis.get("statistics", {})
        
        # Communication (well-documented repos, good descriptions)
        repos_with_descriptions = sum(
            1 for repo in candidate_analysis.get("repositories", [])
            if repo.get("description") and len(repo["description"]) > 20
        )
        score += min(repos_with_descriptions * 5, 25)  # Max 25 points
        
        # Collaboration (followers, forks)
        followers = stats.get("followers", 0)
        score += min(followers * 0.3, 20)  # Max 20 points
        
        # Community engagement (public repos, activity)
        public_repos = profile.get("public_repos", 0)
        score += min(public_repos * 1, 20)  # Max 20 points
        
        # Professional presence (complete profile)
        profile_completeness = sum([
            bool(profile.get("name")),
            bool(profile.get("bio")),
            bool(profile.get("company")),
            bool(profile.get("location")),
            bool(profile.get("blog"))
        ])
        score += profile_completeness * 7  # 7 points each, max 35
        
        return min(score, 100)
    
    def match_candidate(
        self,
        candidate_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> CandidateScore:
        """
        Match a candidate against job requirements and calculate fit score.
        
        Args:
            candidate_analysis (dict): GitHub candidate analysis
            job_analysis (dict): Job requirements analysis
            
        Returns:
            CandidateScore object with detailed scoring
        """
        username = candidate_analysis.get("username", "unknown")
        self.logger.info(f"Matching candidate: {username}")
        
        # Extract required skills
        required_skills = self._extract_required_skills(job_analysis)
        
        # Calculate component scores
        tech_score, matched, missing, bonus = self._calculate_technical_skills_score(
            candidate_analysis, required_skills
        )
        
        exp_score = self._calculate_experience_score(candidate_analysis, job_analysis)
        activity_score = self._calculate_activity_score(candidate_analysis)
        edu_score = self._calculate_education_score(candidate_analysis, job_analysis)
        soft_score = self._calculate_soft_skills_score(candidate_analysis, job_analysis)
        
        # Calculate weighted total score
        total_score = (
            tech_score * self.component_weights["technical_skills"] +
            exp_score * self.component_weights["experience"] +
            activity_score * self.component_weights["activity"] +
            edu_score * self.component_weights["education"] +
            soft_score * self.component_weights["soft_skills"]
        )
        
        # Create result
        result = CandidateScore(
            username=username,
            total_score=round(total_score, 2),
            technical_skills_score=round(tech_score, 2),
            experience_score=round(exp_score, 2),
            activity_score=round(activity_score, 2),
            education_score=round(edu_score, 2),
            soft_skills_score=round(soft_score, 2),
            matched_skills=matched,
            missing_skills=missing,
            bonus_skills=bonus,
            profile_url=candidate_analysis.get("profile", {}).get("profile_url", ""),
            location=candidate_analysis.get("profile", {}).get("location"),
            hireable=candidate_analysis.get("hireable")
        )
        
        self.logger.info(f"Match complete for {username}: {total_score:.2f}/100")
        return result
    
    def rank_candidates(
        self,
        candidates: List[CandidateScore],
        min_score: float = 0.0
    ) -> List[CandidateScore]:
        """
        Rank candidates by total score.
        
        Args:
            candidates (list): List of CandidateScore objects
            min_score (float): Minimum score threshold
            
        Returns:
            Sorted list of candidates
        """
        # Filter by minimum score
        filtered = [c for c in candidates if c.total_score >= min_score]
        
        # Sort by total score (descending)
        ranked = sorted(filtered, key=lambda x: x.total_score, reverse=True)
        
        self.logger.info(f"Ranked {len(ranked)} candidates (min score: {min_score})")
        return ranked