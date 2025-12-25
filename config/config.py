from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool
    # ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "").split(",")

    ALLOWED_HOSTS: List[str]
    # ALLOWED_HOSTS: List[str] = Field(default=["127.0.0.1"])
    # ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["127.0.0.1"])

    # @model_validator(mode="before")
    # def split_hosts(cls, values):
    #     if isinstance(values, str):
    #         return [host.strip() for host in values.split(",") if host.strip()]
    #     return values

    TELEGRAM_TOKEN: str
    CHAT_ID: str

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        env_file_encoding = "utf-8"

    
settings = Settings()