"""Модальное окно / бэк карточки Trello."""

from __future__ import annotations

import allure
from selene import be, browser, have
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class CardPage:
    def open_by_url(self, url: str) -> CardPage:
        with allure.step(f"Открыть карточку по URL: {url}"):
            browser.open(url)
            browser.wait.until(lambda _: "/c/" in (browser.driver.current_url or ""))
            browser.wait.until(lambda _: (browser.driver.title or "").strip().lower() != "trello")
            browser.wait.until(lambda _: self._card_back_ready())
            browser.wait.until(lambda _: self._title_element() is not None)
        return self

    @staticmethod
    def _card_back_ready() -> bool:
        return bool(
            browser.driver.execute_script(
                """
                const root = document.querySelector('#react-root-card-back');
                if (!root) return false;
                return root.querySelector('button, textarea, input, [contenteditable="true"]') !== null;
                """
            )
        )

    @staticmethod
    def _click_first_visible_button_containing(*needles: str) -> None:
        needles_norm = tuple(n.lower() for n in needles if n)
        for el in browser.driver.find_elements(By.XPATH, "//*[self::button or self::a]"):
            try:
                if not el.is_displayed() or not el.is_enabled():
                    continue
                txt = (
                    (el.text or "")
                    + " "
                    + (el.get_attribute("aria-label") or "")
                    + " "
                    + (el.get_attribute("title") or "")
                ).strip().lower()
                if not txt:
                    continue
                if any(n in txt for n in needles_norm):
                    el.click()
                    return
            except Exception:
                continue
        raise AssertionError(f"Не найдена кнопка с текстом: {', '.join(needles)}")

    @staticmethod
    def _title_element():
        # Prefer scoped search (avoid header search input).
        scope_xpath = (
            "//*[@id='react-root-card-back']",
            "//*[@id='layer-manager-card-back']",
            "//*[contains(@class, 'window-overlay')]",
            "//*[@id='trello-board-root']",
        )
        candidates = (
            ".//textarea[contains(@aria-label, 'Название') or contains(@aria-label, 'name') or contains(@aria-label, 'Name')]",
            ".//input[contains(@aria-label, 'Название') or contains(@aria-label, 'name') or contains(@aria-label, 'Name')]",
            ".//*[@contenteditable='true']",
            ".//textarea",
            ".//input",
        )
        for scope in scope_xpath:
            scopes = browser.driver.find_elements(By.XPATH, scope)
            for root in scopes:
                for xp in candidates:
                    for el in root.find_elements(By.XPATH, xp):
                        try:
                            if el.is_displayed() and el.is_enabled():
                                # skip global header search
                                if el.get_attribute("data-testid") == "cross-product-search-input-skeleton":
                                    continue
                                return el
                        except Exception:
                            continue
        return None

    def rename(self, new_name: str) -> CardPage:
        with allure.step(f"Переименовать карточку в «{new_name}»"):
            browser.wait.until(lambda _: self._card_back_ready())
            browser.wait.until(lambda _: self._title_element() is not None)
            title = self._title_element()
            assert title, "Не найдено поле названия карточки"
            title.click()
            title.send_keys(Keys.CONTROL, "a")
            title.send_keys(Keys.BACKSPACE)
            title.send_keys(new_name)
            title.send_keys(Keys.ENTER)
            browser.element(
                (
                    By.XPATH,
                    f"//*[contains(@value, '{new_name}') or contains(normalize-space(.), '{new_name}')]",
                )
            ).should(be.visible)
        return self

    def should_have_title(self, title: str) -> CardPage:
        with allure.step(f"Проверить название карточки «{title}»"):
            el = self._title_element()
            assert el, "Не найдено поле названия карточки"
            assert title in (el.get_attribute("value") or ""), f"Ожидали title='{title}'"
        return self

    def archive(self) -> CardPage:
        """Архивирует карточку (в актуальном Trello это основной UI-способ «удалить» с доски)."""
        with allure.step("Архивировать карточку через UI"):
            browser.wait.until(lambda _: self._card_back_ready())
            title = self._title_element()
            if title:
                ActionChains(browser.driver).click(title).send_keys("c").perform()
            else:
                ActionChains(browser.driver).send_keys("c").perform()

            def _archived() -> bool:
                if "/c/" not in (browser.driver.current_url or ""):
                    return True
                return not CardPage._card_back_ready()

            try:
                browser.wait.until(lambda _: _archived())
            except Exception:
                browser.driver.execute_script(
                    """
                    const btn = document.querySelector('[data-testid="card-back-actions-button"]');
                    if (btn) btn.click();
                    """
                )
                browser.driver.execute_script(
                    """
                    const needles = ['архивировать', 'archive'];
                    const root = document.querySelector('#react-root-card-back') || document;
                    for (const el of root.querySelectorAll('button, a, [role="button"], li')) {
                      const txt = ((el.innerText||'') + ' ' + (el.getAttribute('aria-label')||'')).toLowerCase();
                      if (needles.some(n => txt.includes(n)) && !txt.includes('доск')) {
                        (el.closest('button,a,[role="button"]')||el).click();
                        return true;
                      }
                    }
                    return false;
                    """
                )
                browser.wait.until(lambda _: _archived())
        return self

    def close(self) -> CardPage:
        with allure.step("Закрыть окно карточки"):
            browser.element('[data-testid="card-back-close-button"]').click()
        return self
