"""Allure-вложения для UI-отчёта."""

from __future__ import annotations

from urllib.parse import urlparse

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from ui_utils.video_frames import save_video_frame


def add_screenshot(driver: WebDriver | None, name: str) -> None:
    if driver is None:
        return
    try:
        png = driver.get_screenshot_as_png()
        save_video_frame(png)
        allure.attach(
            png,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


def add_browser_log(driver: WebDriver | None) -> None:
    if driver is None:
        return
    try:
        logs = driver.get_log("browser")
        if not logs:
            return
        body = "\n".join(
            f"{entry.get('level', '')}: {entry.get('message', '')}" for entry in logs[-50:]
        )
        allure.attach(body, name="browser-log", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass


def add_selenoid_video(driver: WebDriver | None, selenoid_url: str | None) -> None:
    if driver is None or not selenoid_url:
        return
    session_id = getattr(driver, "session_id", None)
    if not session_id:
        return
    parsed = urlparse(selenoid_url)
    host = parsed.hostname or "selenoid.autotests.cloud"
    scheme = parsed.scheme or "https"
    video_url = f"{scheme}://{host}/video/{session_id}.mp4"
    allure.attach(
        video_url,
        name="selenoid-video",
        attachment_type=allure.attachment_type.URI_LIST,
    )
