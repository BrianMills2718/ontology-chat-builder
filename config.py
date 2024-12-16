import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_PROVIDER = os.getenv('API_PROVIDER', 'anthropic').lower()
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    @classmethod
    def validate_config(cls):
        if cls.API_PROVIDER not in ['anthropic', 'openai']:
            raise ValueError("API_PROVIDER must be either 'anthropic' or 'openai'")
        
        if cls.API_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic API")
        
        if cls.API_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI API")