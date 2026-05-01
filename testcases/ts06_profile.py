"""
TS-06: Profile Page — UI Unit Tests
Tests profile header, stats, follow/unfollow functionality, and own profile vs other profile UI.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts06_profile.py [BASE_URL]
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
U1 = "p1_" + str(int(time.time()) % 100000)
U2 = "p2_" + str(int(time.time()) % 100000)
PASS = "testing123"

PASS_COUNT = 0
FAIL_COUNT = 0
RESULTS = []

def log(test_id, name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    status = "PASS ✅" if passed else "FAIL ❌"
    if passed:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    msg = f"  [{status}] {test_id}: {name}"
    if detail and not passed:
        msg += f" — {detail}"
    print(msg)
    RESULTS.append((test_id, name, passed, detail))

def register_user(driver, username, password):
    driver.get(f"{BASE_URL}/register")
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

def login_user(driver, username, password):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

def main():
    print(f"\n{'='*60}")
    print(f"  TS-06: PROFILE PAGE")
    print(f"  Target: {BASE_URL}")
    print(f"  Users: {U1}, {U2}")
    print(f"{'='*60}\n")

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1512,900")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(3)

    try:
        # Register both users
        register_user(driver, U1, PASS)
        register_user(driver, U2, PASS)
        
        # Login as User 1
        login_user(driver, U1, PASS)

        # ─────────────────────────────────────────────────────────
        # PRF-01: Header shows username
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/@{U1}")
            header = driver.find_element(By.CSS_SELECTOR, "h1#page-header-text").text.strip()
            # It should be @U1 or similar
            log("PRF-01", "Header shows username", U1.upper() in header, f"header: {header}")
        except Exception as e:
            log("PRF-01", "Header shows username", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-02: Banner + avatar render
        # ─────────────────────────────────────────────────────────
        try:
            banner = driver.find_element(By.CSS_SELECTOR, ".profile-banner")
            avatar = driver.find_element(By.CSS_SELECTOR, ".profile-avatar-large img")
            log("PRF-02", "Banner and avatar render", banner.is_displayed() and avatar.is_displayed())
        except Exception as e:
            log("PRF-02", "Banner + avatar render", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-04: Own profile shows EDIT PROFILE
        # ─────────────────────────────────────────────────────────
        try:
            edit_btn = driver.find_elements(By.XPATH, "//a[contains(text(), 'EDIT PROFILE')]")
            log("PRF-04", "Own profile shows EDIT PROFILE", len(edit_btn) > 0)
        except Exception as e:
            log("PRF-04", "Own profile shows EDIT PROFILE", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-05: Other profile shows FOLLOW
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/@{U2}")
            follow_btn = driver.find_element(By.ID, "follow-btn")
            follow_text = driver.find_element(By.ID, "follow-text").text.strip()
            log("PRF-05", "Other profile shows FOLLOW", follow_btn.is_displayed() and "FOLLOW" in follow_text)
        except Exception as e:
            log("PRF-05", "Other profile shows FOLLOW", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-06: Follow toggles to FOLLOWING
        # ─────────────────────────────────────────────────────────
        try:
            follow_btn.click()
            time.sleep(1)
            follow_text = driver.find_element(By.ID, "follow-text").text.strip()
            follower_count = int(driver.find_element(By.ID, "follower-count").text.strip())
            log("PRF-06", "Follow toggles to FOLLOWING and increments count", 
                "FOLLOWING" in follow_text and follower_count == 1, 
                f"text: {follow_text}, count: {follower_count}")
        except Exception as e:
            log("PRF-06", "Follow toggles to FOLLOWING", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-07: Unfollow toggles to FOLLOW
        # ─────────────────────────────────────────────────────────
        try:
            driver.find_element(By.ID, "follow-btn").click()
            time.sleep(1)
            follow_text = driver.find_element(By.ID, "follow-text").text.strip()
            follower_count = int(driver.find_element(By.ID, "follower-count").text.strip())
            log("PRF-07", "Unfollow toggles to FOLLOW and decrements count", 
                "FOLLOW" in follow_text and follower_count == 0,
                f"text: {follow_text}, count: {follower_count}")
        except Exception as e:
            log("PRF-07", "Unfollow toggles to FOLLOW", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PRF-08: Post cards match homepage style
        # ─────────────────────────────────────────────────────────
        try:
            # Post something as U2 first
            driver.get(f"{BASE_URL}/logout")
            login_user(driver, U2, PASS)
            driver.get(f"{BASE_URL}/")
            driver.find_element(By.ID, "composer-text").send_keys("U2 test post")
            driver.find_element(By.ID, "senddit-btn").click()
            time.sleep(1)
            
            driver.get(f"{BASE_URL}/@{U2}")
            posts = driver.find_elements(By.CSS_SELECTOR, ".post-card")
            log("PRF-08", "Profile shows post cards", len(posts) > 0)
        except Exception as e:
            log("PRF-08", "Post cards on profile", False, str(e)[:80])

    except Exception as e:
        print(f"\n  [FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

    # ── SUMMARY ──────────────────────────────────────────────
    total = PASS_COUNT + FAIL_COUNT
    print(f"\n{'='*60}")
    print(f"  RESULTS: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")
    print(f"{'='*60}")

    if FAIL_COUNT > 0:
        print("\n  Failed tests:")
        for tid, name, passed, detail in RESULTS:
            if not passed:
                print(f"    ❌ {tid}: {name} — {detail}")

    print()
    return 0 if FAIL_COUNT == 0 else 1

if __name__ == "__main__":
    exit(main())
