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
            path = os.path.join(ART_DIR, f"{item.name}.png")
            driver.save_screenshot(path)
