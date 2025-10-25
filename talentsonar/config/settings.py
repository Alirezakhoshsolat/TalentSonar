"""
Configuration management for the HR Job Analysis Engine.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class for managing API keys and settings.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file (str, optional): Path to .env file. Defaults to .env in project root.
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    @property
    def gemini_api_key(self) -> str:
        """
        Get Google Gemini API key from environment variables.
        
        Returns:
            str: API key
            
        Raises:
            ValueError: If API key is not found
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )
        return api_key
    
    @property
    def default_output_dir(self) -> str:
        """Get default output directory for analysis results."""
        return os.getenv('OUTPUT_DIR', 'output')
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def max_retries(self) -> int:
        """Get maximum number of API retries."""
        return int(os.getenv('MAX_RETRIES', '3'))
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            self.gemini_api_key
            return True
        except ValueError:
            return False


# Create a default configuration instance
config = Config()