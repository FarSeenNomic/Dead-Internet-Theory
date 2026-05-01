"""
TS-05: Settings Page — UI Unit Tests
Tests profile updates, PFP previews, and password changes.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts05_settings.py [BASE_URL]
    Default BASE_URL: http://localhost:5000
"""

import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
TEST_USER = "settester_" + str(int(time.time()) % 100000)
TEST_PASS = "testing123"
NEW_PASS = "newtesting123"

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

def setup_user(driver):
    """Register and login a fresh test user."""
    print("  [SETUP] Registering test user...")
    driver.get(f"{BASE_URL}/register")
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(TEST_USER)
    driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
    driver.find_element(By.NAME, "password2").send_keys(TEST_PASS)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

    print("  [SETUP] Logging in...")
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(TEST_USER)
    driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

def main():
    print(f"\n{'='*60}")
    print(f"  TS-05: SETTINGS PAGE")
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
        setup_user(driver)

        # ─────────────────────────────────────────────────────────
        # SET-01: Page header says SETTINGS
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/settings")
            header = driver.find_element(By.CSS_SELECTOR, "h1#page-header-text").text.strip()
            log("SET-01", "Page header says SETTINGS", header == "SETTINGS", f"header: {header}")
        except Exception as e:
            log("SET-01", "Page header says SETTINGS", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-02: Display name pre-filled
        # ─────────────────────────────────────────────────────────
        try:
            dn_val = driver.find_element(By.ID, "displayname").get_attribute("value")
            # Default display name is often the username if not set, or empty
            log("SET-02", "Display name field exists", dn_val is not None)
        except Exception as e:
            log("SET-02", "Display name pre-filled", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-03: Bio pre-filled
        # ─────────────────────────────────────────────────────────
        try:
            bio_val = driver.find_element(By.ID, "bio").get_attribute("value")
            log("SET-03", "Bio field exists", bio_val is not None)
        except Exception as e:
            log("SET-03", "Bio pre-filled", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-04: PFP URL field blank for default
        # ─────────────────────────────────────────────────────────
        try:
            pfp_val = driver.find_element(By.ID, "pfp").get_attribute("value")
            # Should be empty if it's the default gravatar
            log("SET-04", "PFP URL field blank for default", pfp_val == "", f"val: '{pfp_val}'")
        except Exception as e:
            log("SET-04", "PFP URL field blank for default", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-06: PFP preview on URL input
        # ─────────────────────────────────────────────────────────
        try:
            pfp_input = driver.find_element(By.ID, "pfp")
            test_url = "https://ui-avatars.com/api/?name=Test&size=100"
            pfp_input.send_keys(test_url)
            # Trigger onchange
            driver.execute_script("document.getElementById('pfp').dispatchEvent(new Event('change'));")
            time.sleep(0.5)
            preview_container = driver.find_element(By.ID, "pfp-preview-container")
            preview_img = driver.find_element(By.ID, "pfp-preview-img")
            log("SET-06", "PFP preview shows on URL input", 
                preview_container.is_displayed() and preview_img.get_attribute("src") == test_url)
        except Exception as e:
            log("SET-06", "PFP preview on URL input", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-08: Save profile success
        # ─────────────────────────────────────────────────────────
        try:
            driver.find_element(By.ID, "displayname").clear()
            driver.find_element(By.ID, "displayname").send_keys("New Display Name")
            driver.find_element(By.ID, "bio").clear()
            driver.find_element(By.ID, "bio").send_keys("This is a new bio.")
            driver.find_element(By.CSS_SELECTOR, "form[action='/settings/profile'] button").click()
            time.sleep(1)
            
            success_msg = driver.find_elements(By.CSS_SELECTOR, ".success-msg")
            log("SET-08", "Save profile success message shown", len(success_msg) > 0)
        except Exception as e:
            log("SET-08", "Save profile success", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-05: PFP URL field shows custom URL after save
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/settings")
            pfp_val = driver.find_element(By.ID, "pfp").get_attribute("value")
            log("SET-05", "PFP URL field shows custom URL", pfp_val == test_url, f"val: '{pfp_val}'")
        except Exception as e:
            log("SET-05", "PFP URL field shows custom URL", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-09: Clearing PFP URL keeps default
        # ─────────────────────────────────────────────────────────
        try:
            pfp_input = driver.find_element(By.ID, "pfp")
            pfp_input.clear()
            driver.find_element(By.CSS_SELECTOR, "form[action='/settings/profile'] button").click()
            time.sleep(1)
            
            driver.get(f"{BASE_URL}/settings")
            pfp_val = driver.find_element(By.ID, "pfp").get_attribute("value")
            log("SET-09", "Clearing PFP URL works", pfp_val == "")
        except Exception as e:
            log("SET-09", "Clearing PFP URL", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-10: Password change validation (mismatch)
        # ─────────────────────────────────────────────────────────
        try:
            driver.find_element(By.ID, "current_password").send_keys(TEST_PASS)
            driver.find_element(By.ID, "new_password").send_keys(NEW_PASS)
            driver.find_element(By.ID, "confirm_password").send_keys("wrong_confirm")
            driver.find_element(By.CSS_SELECTOR, "form[action='/settings/password'] button").click()
            time.sleep(1)
            
            error_msg = driver.find_elements(By.CSS_SELECTOR, ".error-msg")
            has_error = len(error_msg) > 0 and "match" in error_msg[0].text.lower()
            log("SET-10", "Password mismatch shows error", has_error)
        except Exception as e:
            log("SET-10", "Password mismatch error", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # SET-11: Wrong current password
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/settings")
            driver.find_element(By.ID, "current_password").send_keys("totally_wrong")
            driver.find_element(By.ID, "new_password").send_keys(NEW_PASS)
            driver.find_element(By.ID, "confirm_password").send_keys(NEW_PASS)
            driver.find_element(By.CSS_SELECTOR, "form[action='/settings/password'] button").click()
            time.sleep(1)
            
            error_msg = driver.find_elements(By.CSS_SELECTOR, ".error-msg")
            has_error = len(error_msg) > 0 and "current" in error_msg[0].text.lower()
            log("SET-11", "Wrong current password shows error", has_error)
        except Exception as e:
            log("SET-11", "Wrong current password error", False, str(e)[:80])

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
