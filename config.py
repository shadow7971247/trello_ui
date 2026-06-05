"""Конфигурация UI-автотестов Trello (публичные доски, без логина)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote, urlparse, urlunparse

import env_loader  # noqa: F401 — загружает trello_ui/.env

_DEFAULT_SELENOID_HOST = "https://selenoid.autotests.cloud/wd/hub"


def _resolve_selenoid_url() -> str | None:
    """SELENOID_URL целиком или host + login/password из Jenkins Bindings."""
    explicit = os.getenv("SELENOID_URL", "").strip()
    login = (os.getenv("SELENOID_LOGIN") or os.getenv("SELENOID_USER") or "").strip()
    password = os.getenv("SELENOID_PASSWORD", "").strip()

    if login and password:
        base = os.getenv("SELENOID_HOST", _DEFAULT_SELENOID_HOST).strip()
        if not base.startswith("http"):
            base = f"https://{base}"
        if "/wd/hub" not in base:
            base = base.rstrip("/") + "/wd/hub"
        parsed = urlparse(base)
        host = parsed.hostname or "selenoid.autotests.cloud"
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or "/wd/hub"
        netloc = f"{quote(login, safe='')}:{quote(password, safe='')}@{host}{port}"
        return urlunparse((parsed.scheme or "https", netloc, path, "", "", ""))

    if explicit and not explicit.startswith("https://:@") and "://:@" not in explicit:
        parsed = urlparse(explicit)
        if parsed.username or not parsed.hostname:
            return explicit
    return None


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
            selenoid_url=_resolve_selenoid_url(),
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
        if os.getenv("JENKINS_URL") and not self.selenoid_url:
            raise ValueError(
                "На Jenkins нужен Selenoid: задайте SELENOID_LOGIN и SELENOID_PASSWORD "
                "в Build Environment → Bindings (Variable должны совпадать с именами)."
            )


config = UiConfig.from_env()
