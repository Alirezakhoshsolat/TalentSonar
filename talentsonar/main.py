#!/usr/bin/env python3
"""
HR Job Analysis Engine - Main Entry Point

This script provides a command-line interface for analyzing job descriptions
and extracting key elements using Google Gemini 2.5 Flash API.

Usage:
    python main.py --input "job_description.txt" --output "analysis.json"
    python main.py --text "Job description text..." --output "analysis.json"
    python main.py --interactive
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from job_analyzer import JobAnalyzer, create_analyzer
from settings import config


def read_job_description_from_file(file_path: str) -> str:
    """
    Read job description from a text file.
    
    Args:
        file_path (str): Path to the text file containing job description
        
    Returns:
        str: Job description text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Job description file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading job description file: {str(e)}")


def save_analysis_result(result: dict, output_path: str) -> None:
    """
    Save analysis result to a JSON file.
    
    Args:
        result (dict): Analysis result dictionary
        output_path (str): Path to save the JSON file
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis results saved to: {output_path}")


def interactive_mode():
    """Run the analyzer in interactive mode."""
    print("=== HR Job Analysis Engine - Interactive Mode ===")
    print("Enter job description (press Ctrl+D or Ctrl+Z when finished):")
    print("-" * 50)
    
    try:
        # Read multi-line input
        job_description_lines = []
        while True:
            try:
                line = input()
                job_description_lines.append(line)
            except EOFError:
                break
        
        job_description = '\n'.join(job_description_lines).strip()
        
        if not job_description:
            print("No job description provided. Exiting.")
            return
        
        print("\nAnalyzing job description...")
        
        # Initialize analyzer
        analyzer = create_analyzer(config.gemini_api_key)
        
        # Perform analysis
        result = analyzer.analyze_to_json(job_description)
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Ask if user wants to save results
        save_choice = input("\nSave results to file? (y/n): ").lower().strip()
        if save_choice in ['y', 'yes']:
            output_file = input("Enter output filename (default: analysis_result.json): ").strip()
            if not output_file:
                output_file = "analysis_result.json"
            save_analysis_result(result, output_file)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")


def main():
    """Main function for the HR Job Analysis Engine."""
    parser = argparse.ArgumentParser(
        description="HR Job Analysis Engine - Extract key elements from job descriptions using Google Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input job.txt --output analysis.json
  %(prog)s --text "Software Engineer position..." --output result.json  
  %(prog)s --interactive
  %(prog)s --input job.txt  # Output to stdout
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Path to text file containing job description'
    )
    input_group.add_argument(
        '--text', '-t',
        type=str,
        help='Job description text as string'
    )
    input_group.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save JSON analysis result (if not specified, prints to stdout)'
    )
    
    # Configuration options
    parser.add_argument(
        '--api-key',
        type=str,
        help='Google Gemini API key (overrides environment variable)'
    )
    
    args = parser.parse_args()
    
    try:
        # Handle interactive mode
        if args.interactive:
            interactive_mode()
            return
        
        # Validate configuration
        if not config.validate() and not args.api_key:
            print("Error: GEMINI_API_KEY not found in environment variables.")
            print("Please:")
            print("1. Set GEMINI_API_KEY in your environment, or")
            print("2. Create a .env file with your API key, or") 
            print("3. Use --api-key parameter")
            print("\nSee .env.template for configuration format.")
            sys.exit(1)
        
        # Get job description
        if args.input:
            job_description = read_job_description_from_file(args.input)
            print(f"Loaded job description from: {args.input}")
        else:
            job_description = args.text
        
        print("Analyzing job description...")
        
        # Initialize analyzer with API key
        api_key = args.api_key or config.gemini_api_key
        analyzer = create_analyzer(api_key)
        
        # Perform analysis
        result = analyzer.analyze_to_json(job_description)
        
        # Handle output
        if args.output:
            save_analysis_result(result, args.output)
        else:
            # Print to stdout
            print("\nAnalysis Results:")
            print("="*50)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\nAnalysis completed successfully!")
        
    except FileNotFoundError as e:
        print(f"File Error: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Analysis Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()