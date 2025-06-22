from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Auth Database settings
    auth_db_name: str = os.getenv("AUTH_DB_NAME", "auth_db")
    auth_db_user: str = os.getenv("AUTH_DB_USER", "auth_user")
    auth_db_password: str = os.getenv("AUTH_DB_PASSWORD", "auth_pass")
    auth_db_host: str = os.getenv("AUTH_DB_HOST", "localhost")
    auth_db_port: str = os.getenv("AUTH_DB_PORT", "5432")
    
    # JWT settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_change_in_production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = 7
    
    # Application settings
    app_name: str = "Insurance Auth Service"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.auth_db_user}:{self.auth_db_password}@{self.auth_db_host}:{self.auth_db_port}/{self.auth_db_name}"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings() 