from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Main Database settings
    main_db_name: str = os.getenv("MAIN_DB_NAME", "main_db")
    main_db_user: str = os.getenv("MAIN_DB_USER", "main_user")
    main_db_password: str = os.getenv("MAIN_DB_PASSWORD", "main_pass")
    main_db_host: str = os.getenv("MAIN_DB_HOST", "localhost")
    main_db_port: str = os.getenv("MAIN_DB_PORT", "5432")
    
    # Auth service settings
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    
    # Application settings
    app_name: str = "Insurance Management System"
    debug: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.main_db_user}:{self.main_db_password}@{self.main_db_host}:{self.main_db_port}/{self.main_db_name}"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings() 