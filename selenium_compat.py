"""Совместимость Selene 2.x с новым Selenium (удалён html5.application_cache)."""

from __future__ import annotations

import sys
import types


def ensure_selenium_html5_shim() -> None:
    if "selenium.webdriver.common.html5.application_cache" in sys.modules:
        return
    html5_pkg = types.ModuleType("selenium.webdriver.common.html5")
    app_cache_mod = types.ModuleType("selenium.webdriver.common.html5.application_cache")

    class ApplicationCache:
        pass

    app_cache_mod.ApplicationCache = ApplicationCache
    sys.modules["selenium.webdriver.common.html5"] = html5_pkg
    sys.modules["selenium.webdriver.common.html5.application_cache"] = app_cache_mod
