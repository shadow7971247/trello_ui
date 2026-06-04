"""Pytest-фикстуры UI-проекта."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from selenium_compat import ensure_selenium_html5_shim

ensure_selenium_html5_shim()

from selene import browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from api_bridge import ApiConfig, TrelloApiClient
from config import UiConfig, config
from pages.login_page import LoginPage

@pytest.fixture(scope="session")
def ui_config() -> UiConfig:
    config.validate()
    return config


@pytest.fixture(scope="session")
def api_client(ui_config: UiConfig) -> TrelloApiClient:
    api_config = ApiConfig(
        base_url=ui_config.trello_api_base_url,
        api_key=ui_config.trello_api_key,
        api_token=ui_config.trello_api_token,
    )
    api_config.validate()
    return TrelloApiClient(api_config)


@pytest.fixture(scope="session")
def member_username(api_client: TrelloApiClient) -> str:
    return api_client.get_current_user().username


def _create_webdriver(ui_config: UiConfig) -> webdriver.Remote:
    size = f"{ui_config.window_width},{ui_config.window_height}"
    if ui_config.browser == "firefox":
        options = FirefoxOptions()
        if ui_config.headless:
            options.add_argument("-headless")
        if ui_config.selenoid_url:
            options.set_capability("browserName", "firefox")
            return webdriver.Remote(ui_config.selenoid_url, options=options)
        return webdriver.Firefox(options=options)

    options = ChromeOptions()
    if ui_config.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={size}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if ui_config.chrome_user_data_dir and not ui_config.selenoid_url:
        profile = Path(ui_config.chrome_user_data_dir)
        if not profile.is_absolute():
            profile = Path(__file__).resolve().parent / profile
        profile.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={profile}")
    if ui_config.selenoid_url:
        options.set_capability("browserName", "chrome")
        options.set_capability(
            "selenoid:options", {"enableVNC": True, "enableVideo": True}
        )
        return webdriver.Remote(ui_config.selenoid_url, options=options)
    return webdriver.Chrome(options=options)


@pytest.fixture(scope="session", autouse=True)
def browser_session(ui_config: UiConfig) -> Generator[None, None, None]:
    driver = _create_webdriver(ui_config)
    driver.set_window_size(ui_config.window_width, ui_config.window_height)

    browser.config.driver = driver
    browser.config.base_url = ui_config.base_url
    browser.config.timeout = max(ui_config.timeout, 15)

    yield

    try:
        driver.quit()
    except Exception:
        pass


@pytest.fixture(scope="session")
def login_page() -> LoginPage:
    return LoginPage()


@pytest.fixture(scope="session")
def logged_in(ui_config: UiConfig, login_page: LoginPage) -> None:
    login_page.open()
    if not login_page._is_logged_in():
        login_page.login(ui_config.email, ui_config.password)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    driver = getattr(browser, "driver", None)
    if driver is None:
        return
    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass
    try:
        logs = driver.get_log("browser")
        if logs:
            body = "\n".join(f"{e.get('level', '')}: {e.get('message', '')}" for e in logs[-50:])
            allure.attach(body, name="browser-log", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass
    if isinstance(driver, RemoteWebDriver) and config.selenoid_url:
        session_id = driver.session_id
        if session_id:
            video_url = f"{config.selenoid_url.rstrip('/')}/video/{session_id}.mp4"
            allure.attach(
                video_url,
                name="selenoid-video",
                attachment_type=allure.attachment_type.URI_LIST,
            )
