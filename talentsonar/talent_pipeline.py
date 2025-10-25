#!/usr/bin/env python3
"""
Talent Sourcing Pipeline

Main script for discovering and ranking GitHub talent based on job requirements.

Usage:
    python talent_pipeline.py --job-file job.txt --search "language:python location:california"
    python talent_pipeline.py --job-analysis analysis.json --usernames user1 user2 user3
    python talent_pipeline.py --job-file job.txt --auto-search --top 10
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from github_scraper import GitHubScraper
from talent_matcher import TalentMatcher, CandidateScore
from job_analyzer import create_analyzer
from settings import config


def load_job_analysis(file_path: str) -> Dict[str, Any]:
    """Load job analysis from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def analyze_job_description(job_file: str, api_key: str) -> Dict[str, Any]:
    """Analyze job description file."""
    print(f"Analyzing job description from: {job_file}")
    
    with open(job_file, 'r') as f:
        job_description = f.read()
    
    analyzer = create_analyzer(api_key)
    return analyzer.analyze_to_json(job_description)


def build_search_query(job_analysis: Dict[str, Any]) -> str:
    """
    Build GitHub search query from job requirements.
    
    Args:
        job_analysis (dict): Job analysis result
        
    Returns:
        GitHub search query string
    """
    query_parts = []
    
    # Extract top required technical skills
    tech_skills = job_analysis.get("technical_skills", [])
    required_skills = [
        skill["requirement"] for skill in tech_skills 
        if skill["importance"] == "required"
    ][:3]  # Top 3
    
    # Add language filters
    for skill in required_skills:
        skill_lower = skill.lower()
        # Map to GitHub language names
        lang_map = {
            "python": "python",
            "javascript": "javascript",
            "java": "java",
            "typescript": "typescript",
            "go": "go",
            "rust": "rust",
            "ruby": "ruby",
            "php": "php",
            "c++": "cpp",
            "c#": "csharp"
        }
        
        for name, gh_lang in lang_map.items():
            if name in skill_lower:
                query_parts.append(f"language:{gh_lang}")
                break
    
    # Add location if specified
    location = job_analysis.get("location")
    if location:
        # Clean location (just city or state)
        loc_clean = location.split(",")[0].strip().replace(" ", "")
        query_parts.append(f"location:{loc_clean}")
    
    # Add followers filter for quality
    query_parts.append("followers:>=10")
    
    # Add repository count filter
    query_parts.append("repos:>=5")
    
    return " ".join(query_parts)


def main():
    """Main function for talent sourcing pipeline."""
    parser = argparse.ArgumentParser(
        description="Talent Sourcing Pipeline - Find and rank GitHub talent for job positions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for candidates based on job description
  %(prog)s --job-file job.txt --search "language:python location:sanfrancisco" --top 20
  
  # Use pre-analyzed job requirements
  %(prog)s --job-analysis analysis.json --search "language:javascript followers:>=50"
  
  # Analyze specific GitHub users
  %(prog)s --job-file job.txt --usernames torvalds guido gvanrossum
  
  # Auto-generate search query from job requirements
  %(prog)s --job-file job.txt --auto-search --top 15
  
  # Save results to file
  %(prog)s --job-file job.txt --auto-search --output candidates.json
        """
    )
    
    # Job requirement input
    job_group = parser.add_mutually_exclusive_group(required=True)
    job_group.add_argument(
        '--job-file', '-j',
        type=str,
        help='Path to job description text file'
    )
    job_group.add_argument(
        '--job-analysis', '-a',
        type=str,
        help='Path to pre-analyzed job requirements JSON file'
    )
    
    # Candidate source
    candidate_group = parser.add_mutually_exclusive_group(required=True)
    candidate_group.add_argument(
        '--search', '-s',
        type=str,
        help='GitHub user search query'
    )
    candidate_group.add_argument(
        '--usernames', '-u',
        nargs='+',
        help='Specific GitHub usernames to analyze'
    )
    candidate_group.add_argument(
        '--auto-search',
        action='store_true',
        help='Automatically generate search query from job requirements'
    )
    
    # Options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for results (JSON)'
    )
    parser.add_argument(
        '--top', '-t',
        type=int,
        default=10,
        help='Number of top candidates to analyze (default: 10)'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=0.0,
        help='Minimum match score threshold (0-100, default: 0)'
    )
    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub personal access token (for higher rate limits)'
    )
    parser.add_argument(
        '--gemini-api-key',
        type=str,
        help='Google Gemini API key (overrides environment variable)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed scoring'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Get or create job analysis
        print("=" * 60)
        print("TALENT SOURCING PIPELINE")
        print("=" * 60)
        
        if args.job_file:
            # Analyze job description
            gemini_key = args.gemini_api_key or config.gemini_api_key
            job_analysis = analyze_job_description(args.job_file, gemini_key)
            print(f"\n✅ Job analyzed: {job_analysis['job_title']}")
        else:
            # Load pre-analyzed job
            job_analysis = load_job_analysis(args.job_analysis)
            print(f"\n✅ Loaded job analysis: {job_analysis['job_title']}")
        
        # Step 2: Initialize GitHub scraper
        github_token = args.github_token or os.getenv('GITHUB_TOKEN')
        scraper = GitHubScraper(github_token=github_token)
        
        # Check rate limits
        rate_info = scraper.get_rate_limit_status()
        if rate_info:
            core_limit = rate_info.get('resources', {}).get('core', {})
            print(f"GitHub API rate limit: {core_limit.get('remaining', 'N/A')}/{core_limit.get('limit', 'N/A')}")
        
        # Step 3: Get candidate list
        print("\n" + "-" * 60)
        print("FINDING CANDIDATES")
        print("-" * 60)
        
        candidate_usernames = []
        
        if args.usernames:
            # Use provided usernames
            candidate_usernames = args.usernames
            print(f"Analyzing {len(candidate_usernames)} specified users")
        else:
            # Search GitHub
            if args.auto_search:
                search_query = build_search_query(job_analysis)
                print(f"Auto-generated search query: {search_query}")
            else:
                search_query = args.search
                print(f"Search query: {search_query}")
            
            # Perform search
            search_results = scraper.search_users(search_query, max_results=args.top)
            candidate_usernames = [user['username'] for user in search_results]
            print(f"Found {len(candidate_usernames)} candidates from search")
        
        if not candidate_usernames:
            print("No candidates found. Try adjusting your search query.")
            return
        
        # Step 4: Analyze candidates
        print("\n" + "-" * 60)
        print("ANALYZING CANDIDATES")
        print("-" * 60)
        
        candidate_analyses = []
        for i, username in enumerate(candidate_usernames[:args.top], 1):
            print(f"\n[{i}/{min(len(candidate_usernames), args.top)}] Analyzing @{username}...")
            
            analysis = scraper.analyze_candidate_skills(username)
            if "error" not in analysis:
                candidate_analyses.append(analysis)
                print(f"  ✓ Found {len(analysis.get('languages', {}))} languages, "
                      f"{analysis['statistics']['total_repos']} repos")
            else:
                print(f"  ✗ Failed to analyze {username}")
        
        print(f"\n✅ Successfully analyzed {len(candidate_analyses)} candidates")
        
        # Step 5: Match and score candidates
        print("\n" + "-" * 60)
        print("MATCHING CANDIDATES TO JOB")
        print("-" * 60)
        
        matcher = TalentMatcher()
        scored_candidates = []
        
        for analysis in candidate_analyses:
            score = matcher.match_candidate(analysis, job_analysis)
            scored_candidates.append(score)
        
        # Step 6: Rank candidates
        ranked_candidates = matcher.rank_candidates(scored_candidates, min_score=args.min_score)
        
        # Step 7: Display results
        print("\n" + "=" * 60)
        print("RANKED CANDIDATES")
        print("=" * 60)
        
        if not ranked_candidates:
            print(f"\nNo candidates met the minimum score threshold ({args.min_score})")
        else:
            for i, candidate in enumerate(ranked_candidates, 1):
                print(f"\n#{i} - @{candidate.username}")
                print(f"Overall Score: {candidate.total_score:.1f}/100")
                print(f"Profile: {candidate.profile_url}")
                
                if candidate.location:
                    print(f"Location: {candidate.location}")
                if candidate.hireable:
                    print("🟢 Hireable: Yes")
                
                if args.verbose:
                    print(f"\nScore Breakdown:")
                    print(f"  • Technical Skills: {candidate.technical_skills_score:.1f}/100")
                    print(f"  • Experience: {candidate.experience_score:.1f}/100")
                    print(f"  • Activity: {candidate.activity_score:.1f}/100")
                    print(f"  • Education: {candidate.education_score:.1f}/100")
                    print(f"  • Soft Skills: {candidate.soft_skills_score:.1f}/100")
                    
                    if candidate.matched_skills:
                        print(f"\n  ✅ Matched Skills ({len(candidate.matched_skills)}):")
                        for skill in candidate.matched_skills[:10]:
                            print(f"     - {skill}")
                    
                    if candidate.missing_skills:
                        print(f"\n  ❌ Missing Skills ({len(candidate.missing_skills)}):")
                        for skill in candidate.missing_skills[:5]:
                            print(f"     - {skill}")
                    
                    if candidate.bonus_skills:
                        print(f"\n  ⭐ Bonus Skills ({len(candidate.bonus_skills)}):")
                        for skill in candidate.bonus_skills[:5]:
                            print(f"     - {skill}")
                
                print("-" * 60)
        
        # Step 8: Save results if requested
        if args.output:
            results = {
                "job_analysis": {
                    "title": job_analysis["job_title"],
                    "company": job_analysis.get("company"),
                    "location": job_analysis.get("location")
                },
                "search_criteria": args.search or "auto-generated" if args.auto_search else args.usernames,
                "total_candidates_analyzed": len(candidate_analyses),
                "candidates": [candidate.model_dump() for candidate in ranked_candidates],
                "analysis_timestamp": ranked_candidates[0].match_timestamp if ranked_candidates else None
            }
            
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Results saved to: {args.output}")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Job Position: {job_analysis['job_title']}")
        print(f"Candidates Analyzed: {len(candidate_analyses)}")
        print(f"Qualified Candidates (>{args.min_score} score): {len(ranked_candidates)}")
        
        if ranked_candidates:
            avg_score = sum(c.total_score for c in ranked_candidates) / len(ranked_candidates)
            print(f"Average Match Score: {avg_score:.1f}/100")
            print(f"Top Candidate: @{ranked_candidates[0].username} ({ranked_candidates[0].total_score:.1f}/100)")
        
        print("\n✅ Talent sourcing pipeline completed!")
        
    except FileNotFoundError as e:
        print(f"File Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()