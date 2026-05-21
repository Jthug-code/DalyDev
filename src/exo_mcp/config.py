import os
from dataclasses import dataclass


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return int(raw)


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_token: str | None
    timeout_seconds: float
    connect_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        base = os.environ.get("EXO_BASE_URL", "http://127.0.0.1:52415").rstrip("/")
        token = os.environ.get("EXO_API_TOKEN", "").strip() or None
        return cls(
            base_url=base,
            api_token=token,
            timeout_seconds=_env_float("EXO_REQUEST_TIMEOUT", 600.0),
            connect_timeout_seconds=_env_float("EXO_CONNECT_TIMEOUT", 10.0),
        )


def max_events() -> int:
    return max(1, min(_env_int("EXO_MAX_EVENTS", 50), 500))
