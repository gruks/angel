"""
Configuration management for ConflictPulse.

Uses pydantic-settings for environment variable validation and management.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings have sensible defaults for local development.
    Production deployments should override via environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/conflictpulse",
        description="PostgreSQL/TimescaleDB connection string",
    )
    
    # Kafka
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        alias="KAFKA_BOOTSTRAP_SERVERS",
        description="Kafka broker addresses",
    )
    kafka_security_protocol: str = Field(
        default="PLAINTEXT",
        description="Kafka security protocol (PLAINTEXT, SASL_SSL, etc.)",
    )
    
    # Data Source API Keys
    gdelt_api_key: Optional[str] = Field(
        default=None,
        alias="GDELT_API_KEY",
        description="GDELT Cloud API key",
    )
    acled_username: Optional[str] = Field(
        default=None,
        alias="ACLED_USERNAME",
        description="ACLED API username",
    )
    acled_password: Optional[str] = Field(
        default=None,
        alias="ACLED_PASSWORD",
        description="ACLED API password",
    )
    unhcr_api_key: Optional[str] = Field(
        default=None,
        alias="UNHCR_API_KEY",
        description="UNHCR API key",
    )
    
    # Polling Intervals (in seconds)
    # Based on RESEARCH.md recommendations
    gdelt_poll_interval_seconds: int = Field(
        default=900,  # 15 minutes
        description="GDELT poll interval",
    )
    acled_poll_interval_seconds: int = Field(
        default=21600,  # 6 hours
        description="ACLED poll interval",
    )
    unhcr_poll_interval_seconds: int = Field(
        default=43200,  # 12 hours
        description="UNHCR poll interval",
    )
    imf_poll_interval_seconds: int = Field(
        default=86400,  # 1 day
        description="IMF data poll interval",
    )
    worldbank_poll_interval_seconds: int = Field(
        default=86400,  # 1 day
        description="World Bank data poll interval",
    )
    
    # API Server
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    api_reload: bool = Field(
        default=True,
        description="Enable auto-reload for development",
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    
    # Feature Flags
    enable_kafka: bool = Field(
        default=True,
        description="Enable Kafka event streaming",
    )
    enable_timescale: bool = Field(
        default=True,
        description="Enable TimescaleDB time-series features",
    )
    enable_postgis: bool = Field(
        default=True,
        description="Enable PostGIS spatial features",
    )


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the database connection URL."""
    return settings.database_url


def get_kafka_bootstrap_servers() -> str:
    """Get the Kafka bootstrap servers."""
    return settings.kafka_bootstrap_servers


def get_poll_interval(source: str) -> int:
    """Get the poll interval for a specific data source in seconds."""
    interval_map = {
        "gdelt": settings.gdelt_poll_interval_seconds,
        "acled": settings.acled_poll_interval_seconds,
        "unhcr": settings.unhcr_poll_interval_seconds,
        "imf": settings.imf_poll_interval_seconds,
        "worldbank": settings.worldbank_poll_interval_seconds,
    }
    return interval_map.get(source, 3600)  # Default 1 hour


# Export
__all__ = [
    "Settings",
    "settings",
    "get_database_url",
    "get_kafka_bootstrap_servers",
    "get_poll_interval",
]