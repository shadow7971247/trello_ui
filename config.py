"""Конфигурация UI-автотестов Trello (публичные доски, без логина)."""

from __future__ import annotations

import os
from dataclasses import dataclass

import env_loader  # noqa: F401 — загружает trello_ui/.env


@dataclass(frozen=True)
class UiConfig:
    base_url: str
    browser: str
    headless: bool
    timeout: float
    trello_api_key: str
    trello_api_token: str
    trello_api_base_url: str
    selenoid_url: str | None
    window_width: int
    window_height: int

    @classmethod
    def from_env(cls) -> UiConfig:
        return cls(
            base_url=os.getenv("TRELLO_WEB_URL", "https://trello.com").rstrip("/"),
            browser=os.getenv("BROWSER", "chrome").lower(),
            headless=os.getenv("HEADLESS", "false").lower() == "true",
            timeout=float(os.getenv("BROWSER_TIMEOUT", "15")),
            trello_api_key=os.getenv("TRELLO_API_KEY", ""),
            trello_api_token=os.getenv("TRELLO_API_TOKEN", ""),
            trello_api_base_url=os.getenv(
                "TRELLO_BASE_URL", "https://api.trello.com/1"
            ).rstrip("/"),
            selenoid_url=os.getenv("SELENOID_URL") or None,
            window_width=int(os.getenv("BROWSER_WIDTH", "1920")),
            window_height=int(os.getenv("BROWSER_HEIGHT", "1080")),
        )

    def validate(self) -> None:
        missing = [
            name
            for name, value in (
                ("TRELLO_API_KEY", self.trello_api_key),
                ("TRELLO_API_TOKEN", self.trello_api_token),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                f"Не заданы обязательные переменные окружения: {', '.join(missing)}"
            )


config = UiConfig.from_env()
