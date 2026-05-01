"""
TS-04: Authentication Pages — UI Unit Tests
Tests the login and register forms, validation errors, redirects, and session state.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts04_authentication.py [BASE_URL]
    Default BASE_URL: http://localhost:5000
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
TEST_USER = "authtester_" + str(int(time.time()) % 100000)
TEST_PASS = "testing123"

PASS = 0
FAIL = 0
RESULTS = []

def log(test_id, name, passed, detail=""):
    global PASS, FAIL
    status = "PASS ✅" if passed else "FAIL ❌"
    if passed:
        PASS += 1
    else:
        FAIL += 1
    msg = f"  [{status}] {test_id}: {name}"
    if detail and not passed:
        msg += f" — {detail}"
    print(msg)
    RESULTS.append((test_id, name, passed, detail))

def main():
    print(f"\n{'='*60}")
    print(f"  TS-04: AUTHENTICATION")
    print(f"  Target: {BASE_URL}")
    print(f"  Test User: {TEST_USER}")
    print(f"{'='*60}\n")

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1512,900")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(3)
    wait = WebDriverWait(driver, 5)

    try:
        # ─────────────────────────────────────────────────────────
        # AUTH-01: Register page renders
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/register")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            has_username = len(driver.find_elements(By.NAME, "username")) == 1
            has_pwd1 = len(driver.find_elements(By.NAME, "password")) == 1
            has_pwd2 = len(driver.find_elements(By.NAME, "password2")) == 1
            has_btn = len(driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")) == 1
            log("AUTH-01", "Register page renders form fields", 
                has_username and has_pwd1 and has_pwd2 and has_btn,
                f"u:{has_username}, p1:{has_pwd1}, p2:{has_pwd2}, btn:{has_btn}")
        except Exception as e:
            log("AUTH-01", "Register page renders", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-02: Register page title
        # ─────────────────────────────────────────────────────────
        try:
            title = driver.title
            log("AUTH-02", "Register page title is correct", "Register" in title, f"title: {title}")
        except Exception as e:
            log("AUTH-02", "Register page title", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-03: Password mismatch error
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/register")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(f"fail_{TEST_USER}")
            driver.find_element(By.NAME, "password").send_keys("password123")
            driver.find_element(By.NAME, "password2").send_keys("password456")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            error_el = driver.find_elements(By.CSS_SELECTOR, ".auth-error")
            has_error = len(error_el) > 0 and "do not match" in error_el[0].text.lower()
            log("AUTH-03", "Password mismatch shows error", has_error, 
                f"error: {error_el[0].text if len(error_el)>0 else 'None'}")
        except Exception as e:
            log("AUTH-03", "Password mismatch error", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-04: Short password error
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/register")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(f"fail_{TEST_USER}")
            driver.find_element(By.NAME, "password").send_keys("123")
            driver.find_element(By.NAME, "password2").send_keys("123")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            error_el = driver.find_elements(By.CSS_SELECTOR, ".auth-error")
            has_error = len(error_el) > 0 and "between 6" in error_el[0].text.lower()
            log("AUTH-04", "Short password shows error", has_error, 
                f"error: {error_el[0].text if len(error_el)>0 else 'None'}")
        except Exception as e:
            log("AUTH-04", "Short password error", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-06: Successful register → login
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/register")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(TEST_USER)
            driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
            driver.find_element(By.NAME, "password2").send_keys(TEST_PASS)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            # Should be redirected to login page
            is_login = "/login" in driver.current_url
            log("AUTH-06", "Successful register redirects to login", is_login, f"url: {driver.current_url}")
        except Exception as e:
            log("AUTH-06", "Successful register", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-05: Duplicate username error
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/register")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(TEST_USER) # Try registering same user again
            driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
            driver.find_element(By.NAME, "password2").send_keys(TEST_PASS)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            error_el = driver.find_elements(By.CSS_SELECTOR, ".auth-error")
            has_error = len(error_el) > 0 and "taken" in error_el[0].text.lower()
            log("AUTH-05", "Duplicate username shows error", has_error, 
                f"error: {error_el[0].text if len(error_el)>0 else 'None'}")
        except Exception as e:
            log("AUTH-05", "Duplicate username error", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-07: Login page renders
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/login")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            has_username = len(driver.find_elements(By.NAME, "username")) == 1
            has_pwd = len(driver.find_elements(By.NAME, "password")) == 1
            has_btn = len(driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")) == 1
            log("AUTH-07", "Login page renders form fields", 
                has_username and has_pwd and has_btn,
                f"u:{has_username}, p:{has_pwd}, btn:{has_btn}")
        except Exception as e:
            log("AUTH-07", "Login page renders", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-08: Bad credentials error
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/login")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(TEST_USER)
            driver.find_element(By.NAME, "password").send_keys("wrongpassword")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            error_el = driver.find_elements(By.CSS_SELECTOR, ".auth-error")
            has_error = len(error_el) > 0 and "not found" in error_el[0].text.lower()
            log("AUTH-08", "Bad credentials show error", has_error, 
                f"error: {error_el[0].text if len(error_el)>0 else 'None'}")
        except Exception as e:
            log("AUTH-08", "Bad credentials error", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-09: Successful login → home
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/login")
            wait.until(EC.presence_of_element_located((By.NAME, "username")))
            driver.find_element(By.NAME, "username").send_keys(TEST_USER)
            driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(0.5)
            
            # Should be redirected to home page
            is_home = driver.current_url.endswith("/") or driver.current_url.endswith("/explore")
            # Verify nav shows logged-in state
            has_logout = len(driver.find_elements(By.XPATH, "//span[text()='LOGOUT']")) > 0
            
            log("AUTH-09", "Successful login redirects to home", is_home and has_logout, f"url: {driver.current_url}")
        except Exception as e:
            log("AUTH-09", "Successful login", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # AUTH-10: Login/Register cross-links
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/logout") # Ensure logged out
            time.sleep(0.5)
            
            driver.get(f"{BASE_URL}/login")
            to_register = driver.find_element(By.CSS_SELECTOR, ".auth-footer a").get_attribute("href")
            
            driver.get(f"{BASE_URL}/register")
            to_login = driver.find_element(By.CSS_SELECTOR, ".auth-footer a").get_attribute("href")
            
            log("AUTH-10", "Auth pages have cross-links", 
                "/register" in to_register and "/login" in to_login,
                f"login->{to_register}, register->{to_login}")
        except Exception as e:
            log("AUTH-10", "Auth cross-links", False, str(e)[:80])

    except Exception as e:
        print(f"\n  [FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

    # ── SUMMARY ──────────────────────────────────────────────
    total = PASS + FAIL
    print(f"\n{'='*60}")
    print(f"  RESULTS: {PASS}/{total} passed, {FAIL} failed")
    print(f"{'='*60}")

    if FAIL > 0:
        print("\n  Failed tests:")
        for tid, name, passed, detail in RESULTS:
            if not passed:
                print(f"    ❌ {tid}: {name} — {detail}")

    print()
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    exit(main())
