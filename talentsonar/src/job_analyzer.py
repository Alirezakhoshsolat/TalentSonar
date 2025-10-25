"""
HR Job Analysis Engine
A sophisticated engine that processes job descriptions and extracts key elements
using Google Gemini 2.5 Flash API.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import google.generativeai as genai
from datetime import datetime


class JobRequirement(BaseModel):
    """Model for individual job requirements."""
    category: str = Field(..., description="Category of the requirement (e.g., 'technical_skills', 'experience', 'education')")
    requirement: str = Field(..., description="The specific requirement text")
    importance: str = Field(..., description="Importance level: 'required', 'preferred', or 'nice_to_have'")
    years_experience: Optional[int] = Field(None, description="Years of experience if specified")


class JobAnalysisResult(BaseModel):
    """Model for the complete job analysis result."""
    job_title: str = Field(..., description="Extracted job title")
    company: Optional[str] = Field(None, description="Company name if mentioned")
    location: Optional[str] = Field(None, description="Job location if specified")
    employment_type: Optional[str] = Field(None, description="Employment type (full-time, part-time, contract, etc.)")
    salary_range: Optional[str] = Field(None, description="Salary range if mentioned")
    
    # Categorized requirements
    technical_skills: List[JobRequirement] = Field(default_factory=list, description="Technical skills and technologies")
    soft_skills: List[JobRequirement] = Field(default_factory=list, description="Soft skills and interpersonal abilities")
    education: List[JobRequirement] = Field(default_factory=list, description="Educational requirements")
    experience: List[JobRequirement] = Field(default_factory=list, description="Experience requirements")
    certifications: List[JobRequirement] = Field(default_factory=list, description="Required or preferred certifications")
    responsibilities: List[str] = Field(default_factory=list, description="Main job responsibilities")
    
    # Additional metadata
    remote_work_option: Optional[bool] = Field(None, description="Whether remote work is available")
    benefits: List[str] = Field(default_factory=list, description="Mentioned benefits")
    company_culture: List[str] = Field(default_factory=list, description="Company culture aspects mentioned")
    
    # Analysis metadata
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence_score: Optional[float] = Field(None, description="AI confidence in the analysis (0-1)")


class JobAnalyzer:
    """
    Main class for analyzing job descriptions using Google Gemini API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the JobAnalyzer with Google Gemini API key.
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        self.logger = self._setup_logging()
        self._configure_gemini()
    
    def _configure_gemini(self) -> None:
        """Configure the Google Gemini API."""
        try:
            genai.configure(api_key=self.api_key)
            # Use gemini-2.5-flash for optimal performance
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.logger.info("Google Gemini API configured successfully")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the analyzer."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _create_analysis_prompt(self, job_description: str) -> str:
        """
        Create a detailed prompt for the Gemini API to analyze job descriptions.
        
        Args:
            job_description (str): The job description text to analyze
            
        Returns:
            str: Formatted prompt for the AI
        """
        prompt = f"""
        Please analyze the following job description and extract key elements in a structured format. 
        Return your response as a valid JSON object that matches this schema:

        {{
            "job_title": "string - the main job title",
            "company": "string or null - company name if mentioned",
            "location": "string or null - job location",
            "employment_type": "string or null - full-time, part-time, contract, etc.",
            "salary_range": "string or null - salary information if provided",
            
            "technical_skills": [
                {{
                    "category": "technical_skills",
                    "requirement": "specific skill or technology",
                    "importance": "required|preferred|nice_to_have",
                    "years_experience": number or null
                }}
            ],
            "soft_skills": [
                {{
                    "category": "soft_skills", 
                    "requirement": "soft skill description",
                    "importance": "required|preferred|nice_to_have",
                    "years_experience": null
                }}
            ],
            "education": [
                {{
                    "category": "education",
                    "requirement": "educational requirement",
                    "importance": "required|preferred|nice_to_have",
                    "years_experience": null
                }}
            ],
            "experience": [
                {{
                    "category": "experience",
                    "requirement": "experience requirement",
                    "importance": "required|preferred|nice_to_have", 
                    "years_experience": number or null
                }}
            ],
            "certifications": [
                {{
                    "category": "certifications",
                    "requirement": "certification name",
                    "importance": "required|preferred|nice_to_have",
                    "years_experience": null
                }}
            ],
            
            "responsibilities": ["list of main job responsibilities"],
            "remote_work_option": true/false/null,
            "benefits": ["list of mentioned benefits"],
            "company_culture": ["list of company culture aspects"],
            "confidence_score": 0.0-1.0
        }}

        Guidelines for analysis:
        1. Categorize requirements based on their nature (technical, soft skills, education, etc.)
        2. Determine importance levels based on language used (must have, required vs preferred, nice to have)
        3. Extract years of experience when specified
        4. Identify all technical skills, programming languages, frameworks, tools
        5. Note soft skills like communication, leadership, teamwork
        6. Extract educational requirements (degrees, fields of study)
        7. List main responsibilities and duties
        8. Identify benefits, perks, and company culture mentions
        9. Determine if remote work is mentioned
        10. Provide a confidence score based on how clear and detailed the job description is

        Job Description to Analyze:
        {job_description}

        Return only the JSON response, no additional text or formatting.
        """
        return prompt
    
    def analyze_job_description(self, job_description: str) -> JobAnalysisResult:
        """
        Analyze a job description and extract key elements.
        
        Args:
            job_description (str): The job description text to analyze
            
        Returns:
            JobAnalysisResult: Structured analysis results
            
        Raises:
            Exception: If analysis fails
        """
        try:
            self.logger.info("Starting job description analysis")
            
            # Create the prompt
            prompt = self._create_analysis_prompt(job_description)
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            # Check if response exists and has text
            if not response or not hasattr(response, 'text') or not response.text:
                self.logger.error("Empty or invalid response from Gemini API")
                raise Exception("Empty response from AI API")
            
            self.logger.info(f"Received response from AI ({len(response.text)} characters)")
            
            # Parse the JSON response
            try:
                # Clean the response text to remove any markdown formatting
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                response_text = response_text.strip()
                
                analysis_data = json.loads(response_text)
                self.logger.info("Successfully parsed AI response")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {str(e)}")
                self.logger.error(f"Raw response (first 500 chars): {response.text[:500]}")
                raise Exception(f"Invalid JSON response from AI: {str(e)}")
            
            # Validate and create the result object
            result = JobAnalysisResult(**analysis_data)
            
            self.logger.info(f"Analysis completed successfully for job: {result.job_title}")
            return result
            
        except Exception as e:
            self.logger.error(f"Job analysis failed: {str(e)}")
            raise
    
    def analyze_to_json(self, job_description: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze job description and return/save as JSON.
        
        Args:
            job_description (str): Job description text to analyze
            output_file (str, optional): File path to save JSON output
            
        Returns:
            Dict[str, Any]: Analysis results as dictionary
        """
        # Perform analysis
        result = self.analyze_job_description(job_description)
        
        # Convert to dictionary
        result_dict = result.model_dump()
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Analysis results saved to {output_file}")
        
        return result_dict


def create_analyzer(api_key: str) -> JobAnalyzer:
    """
    Factory function to create a JobAnalyzer instance.
    
    Args:
        api_key (str): Google Gemini API key
        
    Returns:
        JobAnalyzer: Configured analyzer instance
    """
    return JobAnalyzer(api_key)