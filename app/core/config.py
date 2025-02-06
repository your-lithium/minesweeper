from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    HOST: str
    PORT: int
    
    FRONTEND_URL: str = None
        
    model_config = SettingsConfigDict(env_file=".env")


settings = AppSettings()
