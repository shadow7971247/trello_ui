"""Pytest-фикстуры UI-проекта (публичные доски, без логина)."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from selenium_compat import ensure_selenium_html5_shim

ensure_selenium_html5_shim()

from selene import browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from api_bridge import ApiConfig, TrelloApiClient, board_name, prepare_public_board
from config import UiConfig
from ui_utils.ui_attach import add_browser_log, add_screenshot, add_selenoid_video

_session_ui_config: UiConfig | None = None


@pytest.fixture(scope="session")
def ui_config() -> UiConfig:
    global _session_ui_config
    config = UiConfig.from_env()
    config.validate()
    _session_ui_config = config
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


@pytest.fixture
def public_test_board(api_client: TrelloApiClient):
    created = []

    def factory(label: str = "Public UI"):
        board = prepare_public_board(api_client, name=board_name(label))
        assert board.url, "API не вернул URL публичной доски"
        created.append(board)
        return board

    yield factory
    for board in created:
        api_client.delete_board(board.id)


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

    driver.quit()


def _report_outcome_label(outcome: str) -> str:
    return {"passed": "успех", "failed": "ошибка", "skipped": "пропуск"}.get(
        outcome, outcome
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    driver = getattr(browser.config, "driver", None)
    if driver is None:
        return
    label = _report_outcome_label(report.outcome)
    add_screenshot(driver, f"{item.name} — {label}")
    add_browser_log(driver)
    if isinstance(driver, RemoteWebDriver) and _session_ui_config and _session_ui_config.selenoid_url:
        add_selenoid_video(driver, _session_ui_config.selenoid_url)
