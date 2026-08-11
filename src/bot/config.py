import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[2]


def _optional_int(value):
    value = (value or "").strip()
    return int(value) if value else None


def _int_list(value):
    value = (value or "").strip()
    return [int(part) for part in value.split(",") if part.strip()]


def _float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Config:
    token: str = ""
    review_channel_id: int | None = None
    log_channel_id: int | None = None
    monitor_channel_ids: list[int] = field(default_factory=list)
    timeout_seconds: int = 600
    umbral_bloqueo: float = 0.80
    umbral_revision: float = 0.50
    db_path: Path = ROOT / "bot.db"
    model_dir: Path = ROOT / "models" / "toxic_transformer"


def load_config() -> Config:
    if load_dotenv:
        load_dotenv(ROOT / ".env")
    return Config(
        token=os.getenv("DISCORD_TOKEN", ""),
        review_channel_id=_optional_int(os.getenv("REVIEW_CHANNEL_ID")),
        log_channel_id=_optional_int(os.getenv("LOG_CHANNEL_ID")),
        monitor_channel_ids=_int_list(os.getenv("MONITOR_CHANNEL_IDS")),
        timeout_seconds=int(_float(os.getenv("TIMEOUT_SECONDS"), 600)),
        umbral_bloqueo=_float(os.getenv("UMBRAL_BLOQUEO"), 0.80),
        umbral_revision=_float(os.getenv("UMBRAL_REVISION"), 0.50),
    )
