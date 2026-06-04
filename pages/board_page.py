"""Страница доски Trello."""

from __future__ import annotations

import time

import allure
from selenium.webdriver.common.by import By
from selene import be, browser, have


class BoardPage:
    _CARD_DIALOG_CSS = "div#layer-manager-card-back, div.window-overlay, div.window[role='dialog']"
    _BOARD_MENU_POPOVER = '[data-testid="board-menu-popover"]'

    def open_by_url(self, url: str) -> BoardPage:
        with allure.step(f"Открыть доску по URL: {url}"):
            browser.open(url)
            browser.element('[data-testid="board-name-display"]').should(be.visible)
        return self

    def should_have_board_title(self, title: str) -> BoardPage:
        with allure.step(f"Проверить заголовок доски «{title}»"):
            browser.element('[data-testid="board-name-display"]').should(have.text(title))
        return self

    def should_have_list(self, list_name: str) -> BoardPage:
        with allure.step(f"Проверить список «{list_name}»"):
            assert self._find_by_testid_text("list", list_name), (
                f"Список «{list_name}» не найден на доске"
            )
        return self

    def should_have_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Проверить карточку «{card_name}» на доске"):
            assert self._find_by_testid_text("card-name", card_name), (
                f"Карточка «{card_name}» не найдена на доске"
            )
        return self

    def should_not_have_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Проверить отсутствие карточки «{card_name}»"):
            for attempt in range(6):
                if not self._find_by_testid_text("card-name", card_name):
                    return self
                if attempt < 5:
                    browser.driver.refresh()
                    browser.element('[data-testid="board-name-display"]').should(be.visible)
                    time.sleep(1)
            raise AssertionError(f"Карточка «{card_name}» всё ещё на доске")
        return self

    def open_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Открыть карточку «{card_name}»"):
            card = self._find_by_testid_text("card-name", card_name)
            assert card, f"Карточка «{card_name}» не найдена"
            # Prefer clicking the card link itself (Trello may route to /c/...).
            link = card
            if getattr(card, "tag_name", "") != "a":
                try:
                    link = card.find_element(By.XPATH, "ancestor-or-self::a[contains(@href, '/c/')]")
                except Exception:
                    link = card
            link.click()

            # Card can open as an overlay or as a routed page; accept both.
            browser.wait.until(
                lambda _: "/c/" in (browser.driver.current_url or "")
                or any(
                    el.is_displayed()
                    for el in browser.driver.find_elements(By.CSS_SELECTOR, self._CARD_DIALOG_CSS)
                )
            )
        return self

    def open_card_by_url(self, url: str) -> BoardPage:
        with allure.step(f"Открыть карточку по URL: {url}"):
            browser.open(url)
            browser.wait.until(lambda _: "/c/" in (browser.driver.current_url or ""))
            browser.wait.until(lambda _: (browser.driver.title or "").strip().lower() != "trello")
            browser.wait.until(
                lambda _: bool(
                    browser.driver.execute_script(
                        """
                        const root = document.querySelector('#react-root-card-back');
                        if (!root) return false;
                        return root.querySelector('input, textarea, button, a') !== null;
                        """
                    )
                )
            )
        return self

    def _open_board_menu(self) -> None:
        opened = browser.driver.execute_script(
            """
            const share = document.querySelector('[data-testid="board-share-button"]');
            let menu = null;
            if (share) {
              const row = share.closest('div')?.parentElement;
              menu = row?.querySelector('button[aria-label="Меню"], button[aria-label="Menu"]');
            }
            if (!menu) {
              const boardRoot = document.querySelector('[data-testid="board-name-display"]')?.closest('#surface');
              const menus = Array.from(document.querySelectorAll('button[aria-label="Меню"], button[aria-label="Menu"]'));
              menu = menus.find(m => !boardRoot || boardRoot.contains(m)) || menus[menus.length - 1];
            }
            if (!menu) return false;
            menu.click();
            return true;
            """
        )
        if not opened:
            raise AssertionError("Не удалось открыть меню доски")
        browser.element(self._BOARD_MENU_POPOVER).should(be.visible)

    def archive_board(self) -> BoardPage:
        with allure.step("Закрыть (архивировать) доску через UI"):
            self._open_board_menu()

            ok_close = browser.driver.execute_script(
                """
                const pop = document.querySelector('[data-testid="board-menu-popover"]');
                if (!pop) return false;
                pop.scrollTop = pop.scrollHeight;
                const match = (el) => {
                  const txt = ((el.innerText||'') + ' ' + (el.getAttribute('aria-label')||'') + ' ' + (el.getAttribute('title')||'')).toLowerCase();
                  return (txt.includes('закрыть доску') || txt.includes('close board'))
                    && !txt.includes('всплывающ');
                };
                const clickTarget = (el) => {
                  const btn = el.closest('button, a, [role="button"]') || el;
                  btn.scrollIntoView({block: 'center'});
                  btn.click();
                  return true;
                };
                for (const el of pop.querySelectorAll('button, a, [role="button"]')) {
                  if (match(el)) return clickTarget(el);
                }
                for (const el of pop.querySelectorAll('div, span, li')) {
                  const raw = (el.innerText || '').trim();
                  if (raw === 'Закрыть доску' || raw === 'Close board') {
                    return clickTarget(el);
                  }
                }
                return false;
                """
            )
            if not ok_close:
                raise AssertionError("Не нашли кнопку «Закрыть доску» в меню доски")

            # Confirm close (you provided stable testid).
            browser.element((By.CSS_SELECTOR, "[data-testid='popover-close-board-confirm']")).should(
                be.visible
            ).click()

            # Debug helper: persist DOM after opening menu
            try:
                from pathlib import Path

                artifacts = Path(__file__).resolve().parent.parent / "artifacts"
                artifacts.mkdir(parents=True, exist_ok=True)
                (artifacts / "debug_board_menu.html").write_text(
                    browser.driver.page_source, encoding="utf-8", errors="ignore"
                )
                items = browser.driver.execute_script(
                    """
                    const pop = document.querySelector('[data-testid="board-menu-popover"]');
                    if (!pop) return [];
                    return Array.from(pop.querySelectorAll('button, a, [role="button"]'))
                      .filter(el => el.offsetParent !== null)
                      .map(el => ((el.innerText||'') + ' | ' + (el.getAttribute('aria-label')||'') + ' | ' + (el.getAttribute('title')||'')).trim())
                      .filter(Boolean)
                      .slice(0, 300);
                    """
                )
                (artifacts / "debug_board_menu_items.txt").write_text(
                    "\n".join(items or []), encoding="utf-8", errors="ignore"
                )
            except Exception:
                pass

        return self

    def delete_closed_board(self) -> BoardPage:
        with allure.step("Удалить закрытую доску навсегда через UI"):
            self._open_board_menu()

            browser.element((By.CSS_SELECTOR, "[data-testid='close-board-delete-board-button']")).should(
                be.visible
            ).click()

            # Last confirm is rendered in a popover/dialog and usually contains "Удалить".
            browser.wait.until(
                lambda _: bool(
                    browser.driver.execute_script(
                        """
                        const needles = ['удалить', 'delete', 'remove'];
                        const dialogs = Array.from(document.querySelectorAll('[role="dialog"], .window-overlay, [data-testid="board-menu-popover"]'));
                        for (const d of dialogs) {
                          const btns = d.querySelectorAll('button, [role="button"], a');
                          for (const b of btns) {
                            const txt = ((b.innerText||'') + ' ' + (b.getAttribute('aria-label')||'') + ' ' + (b.getAttribute('title')||'')).toLowerCase().trim();
                            if (!txt) continue;
                            if (needles.some(n => txt.includes(n))) { b.click(); return true; }
                          }
                        }
                        return false;
                        """
                    )
                )
            )
        return self

    @staticmethod
    def _find_by_testid_text(testid: str, text: str):
        for element in browser.driver.find_elements(
            By.CSS_SELECTOR, f'[data-testid="{testid}"]'
        ):
            if text in (element.text or "") and element.is_displayed():
                return element
        return None
