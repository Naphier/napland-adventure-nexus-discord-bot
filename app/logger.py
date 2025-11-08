import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class Logger:
    """Lightweight logger with dual plaintext/JSON output modes."""

    def __init__(self, source: str | None = None) -> None:
        self._source = self._normalize_source(source)

    def debug(self, message: Any) -> None:
        self._emit("DEBUG", message)

    def info(self, message: Any) -> None:
        self._emit("INFO", message)

    def warning(self, message: Any) -> None:
        self._emit("WARNING", message)

    def error(self, message: Any) -> None:
        self._emit("ERROR", message)

    def critical(self, message: Any) -> None:
        self._emit("CRITICAL", message)

    def _emit(self, level: str, message: Any) -> None:
        serialized = self._serialize(level, message)
        print(serialized)

    def _serialize(self, level: str, message: Any) -> str:
        text = str(message)
        if self._json_mode_enabled():
            return json.dumps(
                {
                    "file_name": self._source,
                    "log_level": level,
                    "message": text,
                }
            )

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-4]
        return f"[{timestamp}][{self._source}][{level}]: {text}"

    def _json_mode_enabled(self) -> bool:
        log_json_env = os.getenv("LOG_JSON", "").lower()
        if log_json_env == "true":
            return True
        return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

    def _normalize_source(self, source: str | None) -> str:
        if not source:
            return "unknown"

        path_guess = Path(source)
        if path_guess.suffix == ".py":
            return path_guess.name

        return source.split(".")[-1]


def get_logger(source: str | None = None) -> Logger:
    return Logger(source)

