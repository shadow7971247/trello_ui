"""Скриншоты шагов UI-тестов."""

from __future__ import annotations

import allure
from selene import browser

from ui_utils.ui_attach import add_screenshot


def capture_step(step_name: str) -> None:
    add_screenshot(browser.driver, step_name)


def step_with_screenshot(step_name: str):
    return allure.step(step_name)
