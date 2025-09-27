from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # IQ Option
    iq_option_email: str
    iq_option_password: str
    iq_option_broker_id: Optional[str] = None
    
    # LLM Configuration
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://ollama:11434"
    gemini_api_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql://user:password@localhost/trading_bot"
    test_database_url: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    log_level: str = "INFO"
    debug: bool = False
    
    # Trading
    default_risk_per_trade: float = 0.02  # 2% risk per trade
    max_daily_risk: float = 0.05  # 5% risk per day
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()