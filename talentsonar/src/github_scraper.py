"""
GitHub Profile Scraper Module

Fetches and analyzes GitHub user profiles, repositories, and activity
to extract candidate information for talent matching.
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter
import time


class GitHubScraper:
    """
    Class for scraping GitHub user profiles and repositories.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub scraper.
        
        Args:
            github_token (str, optional): GitHub personal access token for higher rate limits
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TalentSonar-HR-Engine"
        }
        
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        
        self.logger = self._setup_logging()
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the scraper."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Make a request to GitHub API with rate limit handling.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            
        Returns:
            Response data or None if failed
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params or {})
            
            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 403 and self.rate_limit_remaining == 0:
                reset_time = datetime.fromtimestamp(self.rate_limit_reset)
                self.logger.warning(f"Rate limit exceeded. Resets at {reset_time}")
                return None
            
            if response.status_code == 404:
                self.logger.warning(f"Resource not found: {endpoint}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {endpoint}: {str(e)}")
            return None
    
    def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch GitHub user profile information.
        
        Args:
            username (str): GitHub username
            
        Returns:
            Dictionary containing user profile data
        """
        self.logger.info(f"Fetching profile for user: {username}")
        
        user_data = self._make_request(f"/users/{username}")
        
        if not user_data:
            return None
        
        profile = {
            "username": user_data.get("login"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "email": user_data.get("email"),
            "blog": user_data.get("blog"),
            "twitter": user_data.get("twitter_username"),
            "public_repos": user_data.get("public_repos", 0),
            "public_gists": user_data.get("public_gists", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at"),
            "hireable": user_data.get("hireable"),
            "avatar_url": user_data.get("avatar_url"),
            "profile_url": user_data.get("html_url")
        }
        
        self.logger.info(f"Successfully fetched profile for {username}")
        return profile
    
    def get_user_repositories(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch user's public repositories.
        
        Args:
            username (str): GitHub username
            max_repos (int): Maximum number of repos to fetch
            
        Returns:
            List of repository dictionaries
        """
        self.logger.info(f"Fetching repositories for user: {username}")
        
        repos = []
        page = 1
        per_page = min(100, max_repos)
        
        while len(repos) < max_repos:
            repo_data = self._make_request(
                f"/users/{username}/repos",
                params={
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc"
                }
            )
            
            if not repo_data or len(repo_data) == 0:
                break
            
            for repo in repo_data:
                if len(repos) >= max_repos:
                    break
                
                repos.append({
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "languages_url": repo.get("languages_url"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "watchers": repo.get("watchers_count", 0),
                    "size": repo.get("size", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "topics": repo.get("topics", []),
                    "is_fork": repo.get("fork", False),
                    "url": repo.get("html_url")
                })
            
            page += 1
            
            # Rate limit protection
            if self.rate_limit_remaining and self.rate_limit_remaining < 10:
                self.logger.warning("Approaching rate limit, stopping repo fetch")
                break
        
        self.logger.info(f"Fetched {len(repos)} repositories for {username}")
        return repos
    
    def get_repository_languages(self, languages_url: str) -> Dict[str, int]:
        """
        Fetch languages used in a repository.
        
        Args:
            languages_url (str): API URL for repository languages
            
        Returns:
            Dictionary of language: bytes of code
        """
        # Extract endpoint from full URL
        endpoint = languages_url.replace(self.base_url, "")
        return self._make_request(endpoint) or {}
    
    def analyze_candidate_skills(self, username: str) -> Dict[str, Any]:
        """
        Analyze a GitHub user's skills based on their profile and repositories.
        
        Args:
            username (str): GitHub username
            
        Returns:
            Dictionary containing skill analysis
        """
        self.logger.info(f"Analyzing skills for candidate: {username}")
        
        # Get profile
        profile = self.get_user_profile(username)
        if not profile:
            return {"error": "Failed to fetch user profile"}
        
        # Get repositories
        repos = self.get_user_repositories(username, max_repos=50)
        
        # Analyze languages
        language_stats = Counter()
        total_code_bytes = 0
        
        for repo in repos:
            if repo["is_fork"]:
                continue  # Skip forked repos for more accurate skill assessment
            
            # Get detailed language breakdown
            if repo["languages_url"]:
                languages = self.get_repository_languages(repo["languages_url"])
                for lang, bytes_count in languages.items():
                    language_stats[lang] += bytes_count
                    total_code_bytes += bytes_count
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
        
        # Calculate language percentages
        language_proficiency = {}
        for lang, bytes_count in language_stats.most_common():
            percentage = (bytes_count / total_code_bytes * 100) if total_code_bytes > 0 else 0
            language_proficiency[lang] = {
                "bytes": bytes_count,
                "percentage": round(percentage, 2)
            }
        
        # Extract technologies from repo topics and descriptions
        technologies = set()
        for repo in repos:
            technologies.update(repo.get("topics", []))
            if repo["description"]:
                # Simple keyword extraction (can be enhanced)
                desc_lower = repo["description"].lower()
                tech_keywords = [
                    "react", "vue", "angular", "node", "django", "flask", "fastapi",
                    "docker", "kubernetes", "aws", "azure", "gcp", "tensorflow",
                    "pytorch", "machine learning", "ai", "blockchain", "web3"
                ]
                for keyword in tech_keywords:
                    if keyword in desc_lower:
                        technologies.add(keyword)
        
        # Calculate activity metrics
        total_stars = sum(repo["stars"] for repo in repos)
        total_forks = sum(repo["forks"] for repo in repos)
        original_repos = [r for r in repos if not r["is_fork"]]
        
        # Calculate recency of activity
        if repos:
            latest_push = max(
                (repo["pushed_at"] for repo in repos if repo["pushed_at"]),
                default=None
            )
        else:
            latest_push = None
        
        analysis = {
            "username": username,
            "profile": profile,
            "statistics": {
                "total_repos": len(repos),
                "original_repos": len(original_repos),
                "forked_repos": len(repos) - len(original_repos),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "followers": profile["followers"],
                "total_code_bytes": total_code_bytes
            },
            "languages": language_proficiency,
            "top_languages": list(language_stats.most_common(10)),
            "technologies": list(technologies),
            "repositories": repos[:10],  # Top 10 most recent repos
            "latest_activity": latest_push,
            "hireable": profile["hireable"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Completed skill analysis for {username}")
        return analysis
    
    def search_users(self, query: str, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Search for GitHub users based on criteria.
        
        Args:
            query (str): Search query (e.g., "language:python location:sanfrancisco")
            max_results (int): Maximum number of results to return
            
        Returns:
            List of user profile summaries
        """
        self.logger.info(f"Searching users with query: {query}")
        
        users = []
        page = 1
        per_page = min(100, max_results)
        
        while len(users) < max_results:
            search_data = self._make_request(
                "/search/users",
                params={
                    "q": query,
                    "per_page": per_page,
                    "page": page
                }
            )
            
            if not search_data or "items" not in search_data:
                break
            
            items = search_data["items"]
            if not items:
                break
            
            for user in items:
                if len(users) >= max_results:
                    break
                
                users.append({
                    "username": user.get("login"),
                    "profile_url": user.get("html_url"),
                    "avatar_url": user.get("avatar_url"),
                    "type": user.get("type"),
                    "score": user.get("score")
                })
            
            page += 1
            
            # Rate limit protection
            if self.rate_limit_remaining and self.rate_limit_remaining < 10:
                self.logger.warning("Approaching rate limit, stopping user search")
                break
        
        self.logger.info(f"Found {len(users)} users matching query")
        return users
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        data = self._make_request("/rate_limit")
        return data or {}