from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Youon Intelligence"
    debug: bool = True

settings = Settings()
