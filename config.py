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
        selenoid_url = os.getenv("SELENOID_URL", "").strip() or None
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
            selenoid_url=selenoid_url,
            window_width=int(os.getenv("BROWSER_WIDTH", "1920")),
            window_height=int(os.getenv("BROWSER_HEIGHT", "1080")),
        )

    def validate(self) -> None:
        if not self.trello_api_key:
            raise ValueError("Не задан TRELLO_API_KEY")
        if not self.trello_api_token:
            raise ValueError("Не задан TRELLO_API_TOKEN")
        if os.getenv("JENKINS_URL") and not self.selenoid_url:
            raise ValueError("На Jenkins задайте SELENOID_URL (полный URL Selenoid /wd/hub)")
