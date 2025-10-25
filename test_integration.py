#!/usr/bin/env python
"""
Quick integration test for TalentSonar + Streamlit
Run this to verify everything is working correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from modules.smart_recruiter import SmartRecruiter
        print("✓ SmartRecruiter import successful")
        
        from talentsonar.src.job_analyzer import JobAnalyzer
        print("✓ JobAnalyzer import successful")
        
        from talentsonar.src.github_scraper import GitHubScraper
        print("✓ GitHubScraper import successful")
        
        from talentsonar.src.talent_matcher import TalentMatcher
        print("✓ TalentMatcher import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_initialization():
    """Test that SmartRecruiter can be initialized"""
    print("\nTesting initialization...")
    try:
        from modules.smart_recruiter import SmartRecruiter
        recruiter = SmartRecruiter()
        print("✓ SmartRecruiter initialized successfully")
        print(f"  - Job postings loaded: {len(recruiter.job_postings)}")
        print(f"  - Candidates loaded: {len(recruiter.candidates)}")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_api_keys():
    """Test that API keys are configured"""
    print("\nChecking API keys...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if gemini_key:
        print(f"✓ GEMINI_API_KEY configured (length: {len(gemini_key)})")
    else:
        print("✗ GEMINI_API_KEY not found in .env")
    
    if github_token:
        print(f"✓ GITHUB_TOKEN configured (length: {len(github_token)})")
    else:
        print("✗ GITHUB_TOKEN not found in .env")
    
    return bool(gemini_key and github_token)

def test_job_analysis():
    """Test job description analysis"""
    print("\nTesting job analysis...")
    try:
        from modules.smart_recruiter import SmartRecruiter
        recruiter = SmartRecruiter()
        
        test_job = """
        Senior Python Developer
        
        We're looking for an experienced Python developer with:
        - 5+ years of Python experience
        - Strong knowledge of Django and FastAPI
        - Experience with AWS and Docker
        - PostgreSQL database skills
        """
        
        result = recruiter.parse_job_requirements(test_job)
        print("✓ Job analysis completed")
        print(f"  - Technical skills found: {result.get('technical', [])}")
        print(f"  - Experience years: {result.get('experience_years', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Job analysis failed: {e}")
        return False

def test_github_scraper_methods():
    """Test that GitHubScraper has the correct methods"""
    print("\nTesting GitHubScraper API...")
    try:
        from talentsonar.src.github_scraper import GitHubScraper
        
        # Check that the correct methods exist
        required_methods = ['search_users', 'analyze_candidate_skills', 'get_user_profile']
        scraper = GitHubScraper(github_token=os.getenv("GITHUB_TOKEN"))
        
        for method in required_methods:
            if hasattr(scraper, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' NOT FOUND")
                return False
        
        # Verify that the wrong method doesn't exist
        if hasattr(scraper, 'search_users_by_skill'):
            print("✗ WARNING: Old method 'search_users_by_skill' still exists (should be removed)")
        else:
            print("✓ Confirmed: 'search_users_by_skill' does not exist (correct)")
        
        return True
    except Exception as e:
        print(f"✗ GitHubScraper test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TalentSonar Integration Test Suite")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Initialization": test_initialization(),
        "API Keys": test_api_keys(),
        "Job Analysis": test_job_analysis(),
        "GitHub Scraper API": test_github_scraper_methods()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! Integration is working correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
