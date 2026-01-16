import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Make base URL configurable (CI-friendly)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:3000")

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=options)
    d.set_page_load_timeout(30)
    yield d
    d.quit()


def login_as(driver, wait, username_val="viewer", password_val="viewer123"):
    wait = WebDriverWait(driver, 40)
    driver.get(f"{BASE_URL}/login")

    # Clear auth every time to isolate tests
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    driver.delete_all_cookies()
    driver.refresh()

    # Wait for username input to be visible & enabled
    username = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='username']")))
    wait.until(lambda d: username.is_enabled())

    password = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='password']")))

    # Clear + type (helps avoid flaky pre-filled values)
    username.clear()
    username.send_keys(username_val)

    password.clear()
    password.send_keys(password_val)

    # Click login button when clickable
    login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-btn']")))
  
    login_btn.click()
    
    try:
        wait.until(EC.url_contains("/jobs"))
    except Exception:
        print("\n[DEBUG] Login did not navigate to /jobs")
        print("[DEBUG] Current URL:", driver.current_url)
        print("[DEBUG] Page title:", driver.title)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("[DEBUG] Body text (first 500 chars):", body_text[:500])
        raise
    
    # Stronger than URL check: wait for Jobs page element
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='job-input']")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='jobs-table']")))



def test_success_submit_job(driver):
    wait = WebDriverWait(driver, 20)
    login_as(driver, wait)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table")))
 
    # Wait for navigation to /jobs (URL contains jobs) OR the Jobs header to appear
    wait.until(EC.url_contains("/jobs"))

    # Now submit a job on Jobs page
    # Use a stable selector: ideally add data-testid in the UI, but for now use the first visible input.
    job_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,  "[data-testid='job-input']")))
    job_input.clear()
    job_input.send_keys("selenium job")

    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='submit-job']")))
    submit_btn.click()

    # Validate table renders (job list)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='jobs-table']")))

def test_failed_submit_job(driver):
    wait = WebDriverWait(driver, 20)
    login_as(driver, wait)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table")))
 
    # Wait for navigation to /jobs (URL contains jobs) OR the Jobs header to appear
    wait.until(EC.url_contains("/jobs"))

    # Now submit a job on Jobs page
    # Use a stable selector: ideally add data-testid in the UI, but for now use the first visible input.
    job_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,  "[data-testid='job-input']")))
    job_input.clear()
    job_input.send_keys("crash")

    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='submit-job']")))
    submit_btn.click()

    # Validate table renders (job list)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='jobs-table']")))


def test_queued_submit_job(driver):
    wait = WebDriverWait(driver, 20)
    login_as(driver, wait)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table")))
 
    # Wait for navigation to /jobs (URL contains jobs) OR the Jobs header to appear
    wait.until(EC.url_contains("/jobs"))

    # Now submit a job on Jobs page
    # Use a stable selector: ideally add data-testid in the UI, but for now use the first visible input.
    job_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,  "[data-testid='job-input']")))
    job_input.clear()
    job_input.send_keys("queued")

    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='submit-job']")))
    submit_btn.click()

    # Validate table renders (job list)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='jobs-table']")))