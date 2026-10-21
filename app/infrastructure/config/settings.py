"""Application settings loaded from environment variables.

Uses Pydantic Settings v2 to validate and load configuration from a ``.env``
file. This module is the only place where credentials are read; they are
never hardcoded and never exposed through the HTTP API.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Diferenzzia API.

    Attributes:
        api_key: Secret used to protect administrative endpoints.
        allowed_origins: Comma-separated list of allowed CORS origins.
        cache_ttl_hours: Cache time-to-live in hours.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(..., description="API key for admin endpoints")
    allowed_origins: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )
    cache_ttl_hours: int = Field(
        default=24, ge=1, description="Cache TTL in hours"
    )

    @field_validator("api_key")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        """Ensure required string settings are not empty.

        Args:
            value: Raw setting value.

        Returns:
            The trimmed value.

        Raises:
            ValueError: If the value is empty.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return ``allowed_origins`` as a clean list of origins.

        Returns:
            List of origin strings with whitespace stripped.
        """
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance.

    Returns:
        The process-wide settings singleton.
    """
    return Settings()  # type: ignore[call-arg]
