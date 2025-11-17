"""
All settings – Pydantic v2 + pydantic-settings
"""
from __future__ import annotations

import os
from typing import List, Any, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import Field, ValidationError, field_validator
from loguru import logger
from dotenv import load_dotenv

load_dotenv(override=True)

if os.getenv("DEBUG", "false").lower() == "true":
    print("DEBUG ENV:")
    print("MONGO_URI =", os.getenv("MONGO_URI"))
    print("DB_NAME =", os.getenv("DB_NAME"))
    print("CORS =", os.getenv("BACKEND_CORS_ORIGINS"))


class CustomEnvSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(self, field_name: str, field: Any) -> tuple[Any, str, bool]:
        env_value = os.getenv(field_name)
        if field_name == "BACKEND_CORS_ORIGINS" and env_value:
            # Parse comma-separated string directly for BACKEND_CORS_ORIGINS
            return [o.strip() for o in env_value.split(",") if o.strip()], field_name, False
        return env_value, field_name, False  # False disables JSON parsing

    def __call__(self) -> Dict[str, Any]:
        d = {}
        for field_name in self.settings_cls.__fields__:
            env_val, key, _ = self.get_field_value(field_name, None)
            if env_val is not None:
                d[field_name] = env_val
        return d


class Settings(BaseSettings):
    PROJECT_NAME: str = "Faircruit"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_PRIVATE_KEY: str = Field(..., env="JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: str = Field(..., env="JWT_PUBLIC_KEY")
    MONGO_URI: str = Field(..., env="MONGO_URI")
    DB_NAME: str = "faircruit_db"
    GEMINI_API_KEY: str | None = Field(default=None, env="GEMINI_API_KEY")
    ML_SERVICE_BASE_URL: str = Field(default="", env="ML_SERVICE_BASE_URL")
    ML_API_KEY: str = Field(default="", env="ML_API_KEY")
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173"], env="BACKEND_CORS_ORIGINS")
    MAX_UPLOAD_SIZE_BYTES: int = Field(default=5242880, env="MAX_UPLOAD_SIZE_BYTES")
    WS_MAX_MESSAGE_SIZE: int = Field(default=2000, env="WS_MAX_MESSAGE_SIZE")
    WS_MAX_CONTENT_LENGTH: int = Field(default=2000, env="WS_MAX_CONTENT_LENGTH")
    USE_LOCAL_ML: bool = Field(default=True, env="USE_LOCAL_ML")
    CV_MODEL: str = Field(default="gemini-2.0-flash", env="CV_MODEL")
    CODE_MODEL: str = Field(default="microsoft/codebert-base", env="CODE_MODEL")
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    AWARENESS_WEIGHT: float = Field(default=0.8, env="AWARENESS_WEIGHT")
    APPLICATION_WEIGHT: float = Field(default=1.0, env="APPLICATION_WEIGHT")
    ANALYSIS_WEIGHT: float = Field(default=1.2, env="ANALYSIS_WEIGHT")
    SYNTHESIS_WEIGHT: float = Field(default=1.5, env="SYNTHESIS_WEIGHT")
    MASTERY_WEIGHT: float = Field(default=2.0, env="MASTERY_WEIGHT")
    PASS_THRESHOLD: float = Field(default=0.7, env="PASS_THRESHOLD")
    ADVANCEMENT_THRESHOLD: float = Field(default=0.85, env="ADVANCEMENT_THRESHOLD")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (CustomEnvSettingsSource(settings_cls),)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
    )


# --------------------------------------------------------------------------- #
# Validate on import – fail fast
# --------------------------------------------------------------------------- #
try:
    logger.info("BACKEND_CORS_ORIGINS from env: {}", os.getenv("BACKEND_CORS_ORIGINS"))
    settings = Settings()
    logger.info("Settings loaded (Pydantic v2 + pydantic-settings)")
except ValidationError as exc:
    logger.error("Settings validation failed: {}", exc)
    raise