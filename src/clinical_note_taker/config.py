from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parent
AGENT_WORKSPACE = PACKAGE_ROOT / "resources" / "agent_workspace"

# pydantic-settings' env_file loading below only populates *this* model's own
# (CNT_-prefixed) fields — it never touches os.environ. But the Claude Agent
# SDK spawns the bundled Claude Code CLI as a subprocess that inherits
# os.environ directly, so ANTHROPIC_API_KEY (unprefixed, not one of our
# Settings fields) needs to actually land there or the subprocess silently
# fails to authenticate. load_dotenv() is a no-op if .env doesn't exist.
load_dotenv()


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
    max_turns: int = Field(
        default=8,
        description=(
            "Cap on agent turns per encounter, for the whole session — every "
            "submit_clinical_note retry (see max_submission_attempts) shares this same "
            "budget, since retries are follow-up queries in the same session rather than "
            "separate ones. Not yet reconciled/tested against low values that could hit "
            "this cap mid-retry."
        ),
    )
    max_submission_attempts: int = Field(
        default=2,
        ge=1,
        description=(
            "How many times the agent will ask the model to (re)submit a note before "
            "giving up — covers both a missing submission and one that fails schema "
            "validation. Each retry feeds the specific error back to the model."
        ),
    )
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
