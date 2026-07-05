from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parent
AGENT_WORKSPACE = PACKAGE_ROOT / "resources" / "agent_workspace"


class Settings(BaseSettings):
    """Runtime configuration, loaded from environment variables / `.env`.

    No client- or patient-identifying information should ever be stored
    here — this is process configuration only.
    """

    model_config = SettingsConfigDict(env_prefix="CNT_", env_file=".env", extra="ignore")

    anthropic_model: str = Field(
        default="claude-sonnet-5",
        description="Model used for note generation.",
    )
    max_turns: int = Field(default=8, description="Cap on agent turns per encounter.")
    log_level: str = Field(default="INFO")
    redact_pii_in_logs: bool = Field(
        default=True,
        description=(
            "If true, log output is scrubbed of likely client (owner) PII "
            "before being written anywhere."
        ),
    )
    require_clinician_review: bool = Field(
        default=True,
        description=(
            "If true, every generated note is tagged as a draft requiring "
            "veterinarian sign-off before it can be treated as part of the "
            "medical record."
        ),
    )


def get_settings() -> Settings:
    return Settings()
