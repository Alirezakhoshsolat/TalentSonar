#!/usr/bin/env python3
"""
Example usage of the HR Job Analysis Engine.

This script demonstrates various ways to use the job analyzer programmatically.
"""

import os
import sys
import json
from pathlib import Path

# Add paths to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from job_analyzer import create_analyzer
from settings import config


def example_analyze_from_file():
    """Example: Analyze job description from a text file."""
    print("=== Example 1: Analyzing job description from file ===")
    
    try:
        # Initialize analyzer
        analyzer = create_analyzer(config.gemini_api_key)
        
        # Path to sample job description
        sample_file = os.path.join(os.path.dirname(__file__), 'sample_job_description.txt')
        
        # Read job description
        with open(sample_file, 'r', encoding='utf-8') as f:
            job_description = f.read()
        
        print(f"Analyzing job description from: {sample_file}")
        
        # Perform analysis
        result = analyzer.analyze_to_json(job_description)
        
        # Display results
        print(f"Job Title: {result['job_title']}")
        print(f"Company: {result['company']}")
        print(f"Location: {result['location']}")
        print(f"Technical Skills Found: {len(result['technical_skills'])}")
        print(f"Soft Skills Found: {len(result['soft_skills'])}")
        print(f"Education Requirements: {len(result['education'])}")
        print(f"Experience Requirements: {len(result['experience'])}")
        
        # Save results
        output_file = os.path.join(os.path.dirname(__file__), 'sample_analysis_result.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Full analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"Error in example 1: {str(e)}")


def example_analyze_from_text():
    """Example: Analyze job description from text string."""
    print("\n=== Example 2: Analyzing job description from text string ===")
    
    job_description = """
    Data Scientist Position
    
    We're looking for a passionate Data Scientist to join our AI team.
    
    Requirements:
    - PhD in Statistics, Mathematics, or Computer Science
    - 3+ years of experience in machine learning
    - Proficiency in Python, R, and SQL
    - Experience with TensorFlow, PyTorch, or scikit-learn
    - Strong statistical analysis skills
    - Excellent communication skills
    
    Responsibilities:
    - Develop predictive models and algorithms
    - Analyze large datasets to extract insights
    - Collaborate with engineering teams
    - Present findings to stakeholders
    
    Benefits:
    - Competitive salary $130k-$200k
    - Stock options
    - Remote work available
    """
    
    try:
        # Initialize analyzer
        analyzer = create_analyzer(config.gemini_api_key)
        
        print("Analyzing provided job description text...")
        
        # Perform analysis
        result = analyzer.analyze_to_json(job_description)
        
        # Display key findings
        print(f"Job Title: {result['job_title']}")
        print(f"Salary Range: {result['salary_range']}")
        print(f"Remote Work: {result['remote_work_option']}")
        
        print("\nTechnical Skills:")
        for skill in result['technical_skills']:
            print(f"  - {skill['requirement']} ({skill['importance']})")
        
        print("\nEducation Requirements:")
        for edu in result['education']:
            print(f"  - {edu['requirement']} ({edu['importance']})")
        
    except Exception as e:
        print(f"Error in example 2: {str(e)}")


def example_detailed_analysis():
    """Example: Show detailed analysis breakdown."""
    print("\n=== Example 3: Detailed analysis breakdown ===")
    
    job_description = """
    Marketing Manager - Digital Growth
    
    Join our fast-growing startup as a Marketing Manager focused on digital growth strategies.
    
    Must Have:
    - Bachelor's degree in Marketing or Business
    - 5+ years digital marketing experience
    - Google Ads and Facebook Ads certification required
    - Experience with marketing automation tools (HubSpot, Marketo)
    - Strong analytical skills and data-driven mindset
    
    Nice to Have:
    - MBA preferred
    - Experience with A/B testing platforms
    - SQL knowledge for data analysis
    - Experience in B2B SaaS companies
    
    Offer:
    - $80,000 - $120,000 base salary
    - Performance bonuses
    - Equity package
    - Health insurance
    - Flexible work arrangements
    """
    
    try:
        # Initialize analyzer
        analyzer = create_analyzer(config.gemini_api_key)
        
        # Perform analysis
        result = analyzer.analyze_job_description(job_description)
        
        print("=== DETAILED ANALYSIS BREAKDOWN ===")
        print(f"Position: {result.job_title}")
        print(f"Employment Type: {result.employment_type}")
        print(f"Salary: {result.salary_range}")
        print(f"Remote Options: {result.remote_work_option}")
        print(f"Analysis Confidence: {result.confidence_score}")
        
        print(f"\n--- REQUIREMENTS BY CATEGORY ---")
        
        categories = [
            ('Technical Skills', result.technical_skills),
            ('Soft Skills', result.soft_skills), 
            ('Education', result.education),
            ('Experience', result.experience),
            ('Certifications', result.certifications)
        ]
        
        for category_name, requirements in categories:
            if requirements:
                print(f"\n{category_name}:")
                for req in requirements:
                    experience = f" ({req.years_experience} years)" if req.years_experience else ""
                    print(f"  • {req.requirement}{experience} - {req.importance.upper()}")
        
        if result.responsibilities:
            print(f"\n--- KEY RESPONSIBILITIES ---")
            for i, resp in enumerate(result.responsibilities, 1):
                print(f"{i}. {resp}")
        
        if result.benefits:
            print(f"\n--- BENEFITS & PERKS ---")
            for benefit in result.benefits:
                print(f"  • {benefit}")
        
    except Exception as e:
        print(f"Error in example 3: {str(e)}")


def main():
    """Run all examples."""
    print("HR Job Analysis Engine - Example Usage")
    print("=" * 50)
    
    # Check if API key is configured
    if not config.validate():
        print("Error: GEMINI_API_KEY not configured.")
        print("Please set your API key in the .env file or environment variables.")
        print("See .env.template for the required format.")
        return
    
    # Run examples
    example_analyze_from_file()
    example_analyze_from_text() 
    example_detailed_analysis()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()