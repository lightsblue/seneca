from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    openai_api_key: SecretStr
    openai_api_base_url: str = "https://api.openai.com/v1"
    
    class Config:
        env_file = ".env"

settings = Settings() 