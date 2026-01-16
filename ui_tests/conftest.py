import os
import pytest

ART_DIR = os.path.join("ui_tests", "artifacts")
os.makedirs(ART_DIR, exist_ok=True)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            # Screenshot
            driver.save_screenshot(os.path.join(ART_DIR, f"{item.name}.png"))

            # URL
            with open(os.path.join(ART_DIR, f"{item.name}.url.txt"), "w") as f:
                f.write(driver.current_url)

            # HTML (first ~200KB)
            html = driver.page_source
            with open(os.path.join(ART_DIR, f"{item.name}.html"), "w", encoding="utf-8") as f:
                f.write(html[:200000])

