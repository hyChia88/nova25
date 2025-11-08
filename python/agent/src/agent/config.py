"""
Configuration for CheatSheet Agent
LLM & rate limit config
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration"""
    api_key: str
    model: str = "openai/gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests_per_minute: int = 20
    max_requests_per_hour: int = 500


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = True


class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv(
            'OPENROUTER_API_KEY', 
            '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'
        )
        
        # Data directory
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            'data'
        )
        
        # LLM configuration
        self.llm = LLMConfig(api_key=self.api_key)
        
        # Rate limiting
        self.rate_limit = RateLimitConfig()
        
        # Server
        self.server = ServerConfig()
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        return cls()


# Global config instance
config = Config.from_env()

