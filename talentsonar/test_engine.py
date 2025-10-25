#!/usr/bin/env python3
"""
Simple test script for the HR Job Analysis Engine.
This script tests basic functionality without requiring an API key.
"""

import os
import sys
import json
from pathlib import Path

# Add paths to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing module imports...")
    
    try:
        import job_analyzer
        print("✅ job_analyzer module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import job_analyzer: {e}")
        return False
    
    try:
        import settings
        print("✅ settings module imported successfully")  
    except ImportError as e:
        print(f"❌ Failed to import settings: {e}")
        return False
    
    return True


def test_models():
    """Test that Pydantic models are defined correctly."""
    print("\nTesting data models...")
    
    try:
        from job_analyzer import JobRequirement, JobAnalysisResult
        
        # Test JobRequirement model
        req = JobRequirement(
            category="technical_skills",
            requirement="Python programming",
            importance="required",
            years_experience=3
        )
        print(f"✅ JobRequirement model works: {req.requirement}")
        
        # Test JobAnalysisResult model  
        result = JobAnalysisResult(
            job_title="Test Engineer",
            technical_skills=[req],
            responsibilities=["Test responsibility"]
        )
        print(f"✅ JobAnalysisResult model works: {result.job_title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading (without requiring actual API key)."""
    print("\nTesting configuration...")
    
    try:
        from settings import Config
        
        # Test config creation
        config = Config()
        print("✅ Config object created successfully")
        
        # Test validation (should fail without API key, which is expected)
        is_valid = config.validate()
        if not is_valid:
            print("⚠️  Config validation failed (expected without API key)")
        else:
            print("✅ Config validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_file_structure():
    """Test that required files and directories exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        '.env.template',
        'src/job_analyzer.py',
        'src/__init__.py', 
        'config/settings.py',
        'config/__init__.py',
        'examples/sample_job_description.txt',
        'examples/example_usage.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def test_sample_data():
    """Test that sample job description is readable."""
    print("\nTesting sample data...")
    
    try:
        sample_file = os.path.join(os.path.dirname(__file__), 'examples', 'sample_job_description.txt')
        
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 100:  # Basic sanity check
            print(f"✅ Sample job description loaded ({len(content)} characters)")
            return True
        else:
            print(f"❌ Sample job description too short ({len(content)} characters)")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load sample data: {e}")
        return False


def main():
    """Run all tests."""
    print("HR Job Analysis Engine - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Data Models", test_models), 
        ("Configuration", test_configuration),
        ("File Structure", test_file_structure),
        ("Sample Data", test_sample_data)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The engine is ready to use.")
        print("\nNext steps:")
        print("1. Add your Google Gemini API key to .env file") 
        print("2. Run: python3 main.py --input examples/sample_job_description.txt")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)