from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application info
    APP_NAME: str = "NetPilot AI"
    VERSION: str = "0.1.0"

    # Author information
    AUTHOR_NAME: str = "Nasser Abdelghani"
    AUTHOR_EMAIL: str = "nasser02@yahoo.com"
    AUTHOR_PHONE: str = "+1(279) 789-3480"

    # Environment
    ENV_NAME: str = "local"

    # API details
    API_V1_STR: str = "/api/v1"

    # Logging level
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
