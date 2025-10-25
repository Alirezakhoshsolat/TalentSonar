#!/usr/bin/env python3
"""
Talent Sourcing Demo

Demonstrates the GitHub talent sourcing capabilities with example searches.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from github_scraper import GitHubScraper
from talent_matcher import TalentMatcher
import json


def demo_profile_analysis():
    """Demonstrate analyzing a single GitHub profile."""
    print("=" * 60)
    print("DEMO 1: Analyzing a GitHub Profile")
    print("=" * 60)
    
    scraper = GitHubScraper()
    
    # Analyze a well-known GitHub user (replace with any username)
    username = "torvalds"  # Linus Torvalds as example
    
    print(f"\nAnalyzing @{username}...")
    analysis = scraper.analyze_candidate_skills(username)
    
    if "error" not in analysis:
        print(f"\n✅ Profile Analysis Complete!")
        print(f"\nUsername: {analysis['username']}")
        print(f"Name: {analysis['profile']['name']}")
        print(f"Location: {analysis['profile']['location']}")
        print(f"Bio: {analysis['profile']['bio']}")
        print(f"\nStatistics:")
        print(f"  Total Repositories: {analysis['statistics']['total_repos']}")
        print(f"  Followers: {analysis['statistics']['followers']}")
        print(f"  Total Stars: {analysis['statistics']['total_stars']}")
        
        print(f"\nTop Languages:")
        for lang, data in list(analysis['languages'].items())[:5]:
            print(f"  • {lang}: {data['percentage']:.1f}%")
        
        print(f"\nTechnologies:")
        for tech in list(analysis['technologies'])[:10]:
            print(f"  • {tech}")
    else:
        print(f"❌ Failed to analyze profile")


def demo_candidate_search():
    """Demonstrate searching for candidates."""
    print("\n\n" + "=" * 60)
    print("DEMO 2: Searching for Python Developers")
    print("=" * 60)
    
    scraper = GitHubScraper()
    
    # Search for Python developers
    query = "language:python followers:>=50 repos:>=10"
    print(f"\nSearch Query: {query}")
    print("Searching GitHub...")
    
    users = scraper.search_users(query, max_results=5)
    
    print(f"\n✅ Found {len(users)} candidates:")
    for i, user in enumerate(users, 1):
        print(f"\n{i}. @{user['username']}")
        print(f"   Profile: {user['profile_url']}")
        print(f"   Search Score: {user['score']:.2f}")


def demo_talent_matching():
    """Demonstrate matching a candidate against job requirements."""
    print("\n\n" + "=" * 60)
    print("DEMO 3: Matching Candidate to Job Requirements")
    print("=" * 60)
    
    # Sample job requirements (simplified)
    job_analysis = {
        "job_title": "Senior Python Developer",
        "technical_skills": [
            {"requirement": "Python", "importance": "required"},
            {"requirement": "Django", "importance": "required"},
            {"requirement": "PostgreSQL", "importance": "required"},
            {"requirement": "Docker", "importance": "preferred"},
            {"requirement": "Kubernetes", "importance": "nice_to_have"}
        ],
        "experience": [
            {"requirement": "Web development", "importance": "required", "years_experience": 5}
        ],
        "soft_skills": [
            {"requirement": "Communication", "importance": "required"}
        ],
        "education": [],
        "certifications": []
    }
    
    print(f"\nJob: {job_analysis['job_title']}")
    print(f"Required Skills: {', '.join([s['requirement'] for s in job_analysis['technical_skills'][:3]])}")
    
    # Analyze a candidate
    scraper = GitHubScraper()
    username = "gvanrossum"  # Guido van Rossum (Python creator) as example
    
    print(f"\nAnalyzing candidate: @{username}...")
    candidate_analysis = scraper.analyze_candidate_skills(username)
    
    if "error" not in candidate_analysis:
        # Match candidate to job
        matcher = TalentMatcher()
        score = matcher.match_candidate(candidate_analysis, job_analysis)
        
        print(f"\n✅ Matching Complete!")
        print(f"\n{'-' * 60}")
        print(f"Candidate: @{score.username}")
        print(f"Overall Match Score: {score.total_score:.1f}/100")
        print(f"{'-' * 60}")
        
        print(f"\nScore Breakdown:")
        print(f"  Technical Skills: {score.technical_skills_score:.1f}/100")
        print(f"  Experience: {score.experience_score:.1f}/100")
        print(f"  Activity: {score.activity_score:.1f}/100")
        print(f"  Education: {score.education_score:.1f}/100")
        print(f"  Soft Skills: {score.soft_skills_score:.1f}/100")
        
        if score.matched_skills:
            print(f"\n✅ Matched Skills:")
            for skill in score.matched_skills[:5]:
                print(f"   • {skill}")
        
        if score.missing_skills:
            print(f"\n❌ Missing Skills:")
            for skill in score.missing_skills[:3]:
                print(f"   • {skill}")
        
        if score.bonus_skills:
            print(f"\n⭐ Bonus Skills:")
            for skill in score.bonus_skills[:5]:
                print(f"   • {skill}")
    else:
        print(f"❌ Failed to analyze candidate")


def demo_rate_limits():
    """Check GitHub API rate limits."""
    print("\n\n" + "=" * 60)
    print("DEMO 4: Checking API Rate Limits")
    print("=" * 60)
    
    scraper = GitHubScraper()
    rate_info = scraper.get_rate_limit_status()
    
    if rate_info and 'resources' in rate_info:
        core = rate_info['resources'].get('core', {})
        search = rate_info['resources'].get('search', {})
        
        print(f"\nCore API:")
        print(f"  Limit: {core.get('limit', 'N/A')}")
        print(f"  Remaining: {core.get('remaining', 'N/A')}")
        print(f"  Resets at: {core.get('reset', 'N/A')}")
        
        print(f"\nSearch API:")
        print(f"  Limit: {search.get('limit', 'N/A')}")
        print(f"  Remaining: {search.get('remaining', 'N/A')}")
        
        if core.get('remaining', 0) < 10:
            print(f"\n⚠️ Warning: Low API rate limit remaining!")
            print(f"   Consider adding a GitHub token for higher limits.")
    else:
        print("Unable to fetch rate limit information")


def main():
    """Run all demos."""
    print("\n")
    print("🎯 " + "=" * 58 + " 🎯")
    print("   TALENTSONAR - GITHUB TALENT SOURCING DEMO")
    print("🎯 " + "=" * 58 + " 🎯")
    
    print("\nThis demo will showcase the GitHub talent sourcing capabilities.")
    print("Note: Some demos use well-known GitHub accounts as examples.")
    
    try:
        # Run demos
        demo_rate_limits()
        demo_profile_analysis()
        demo_candidate_search()
        demo_talent_matching()
        
        print("\n\n" + "=" * 60)
        print("✅ Demo Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Try the full pipeline: python talent_pipeline.py --help")
        print("2. Read TALENT_SOURCING.md for detailed documentation")
        print("3. Add your GitHub token to .env for higher rate limits")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check your internet connection")
        print("- Ensure you have the required dependencies installed")
        print("- GitHub API may be rate-limited (add token to .env)")


if __name__ == "__main__":
    main()