"""
TS-01: Sidebar Navigation — UI Unit Tests
Tests the sidebar nav active states, logged-in vs logged-out behavior, and link correctness.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts01_sidebar_navigation.py [BASE_URL]
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
TEST_USER = "navtester_" + str(int(time.time()) % 100000)
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

def get_active_nav(driver):
    """Return the text of the currently active nav item, or None."""
    try:
        active = driver.find_element(By.CSS_SELECTOR, ".nav-item.active")
        return active.text.strip()
    except:
        return None

def get_all_nav_labels(driver):
    """Return all visible nav item labels."""
    items = driver.find_elements(By.CSS_SELECTOR, ".nav-item")
    return [item.text.strip() for item in items if item.text.strip()]

def get_active_nav_style(driver):
    """Return the border-left color of the active nav item."""
    try:
        active = driver.find_element(By.CSS_SELECTOR, ".nav-item.active")
        return active.value_of_css_property("border-left-color")
    except:
        return None

def count_active_navs(driver):
    """Return the number of nav items with the 'active' class."""
    return len(driver.find_elements(By.CSS_SELECTOR, ".nav-item.active"))


def main():
    print(f"\n{'='*60}")
    print(f"  TS-01: SIDEBAR NAVIGATION")
    print(f"  Target: {BASE_URL}")
    print(f"  Test User: {TEST_USER}")
    print(f"{'='*60}\n")

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1512,900")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(3)

    try:
        # ── SETUP: Register + Login ──────────────────────────────
        print("  [SETUP] Registering test user...")
        driver.get(f"{BASE_URL}/register")
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(TEST_USER)
        driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
        driver.find_element(By.NAME, "password2").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # ── NAV-09: Logged-out nav ───────────────────────────────
        # After register, we're on the login page (not logged in yet)
        nav_labels = get_all_nav_labels(driver)
        has_login = "LOGIN" in nav_labels
        has_register = "REGISTER" in nav_labels
        no_replies = "REPLIES" not in nav_labels
        no_profile = "PROFILE" not in nav_labels
        no_settings = "SETTINGS" not in nav_labels
        no_logout = "LOGOUT" not in nav_labels
        log("NAV-09", "Logged-out nav shows LOGIN + REGISTER only",
            has_login and has_register and no_replies and no_profile and no_settings and no_logout,
            f"Got: {nav_labels}")

        # ── Login ────────────────────────────────────────────────
        print("  [SETUP] Logging in...")
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys(TEST_USER)
        driver.find_element(By.NAME, "password").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(0.5)

        # ── NAV-10: Logged-in nav shows full items ───────────────
        nav_labels = get_all_nav_labels(driver)
        has_home = "HOME" in nav_labels
        has_explore = "EXPLORE" in nav_labels
        has_replies = "REPLIES" in nav_labels
        has_profile = "PROFILE" in nav_labels
        has_settings = "SETTINGS" in nav_labels
        has_logout = "LOGOUT" in nav_labels
        no_login = "LOGIN" not in nav_labels
        no_register = "REGISTER" not in nav_labels
        log("NAV-10", "Logged-in nav shows full items",
            has_home and has_explore and has_replies and has_profile and has_settings and has_logout and no_login and no_register,
            f"Got: {nav_labels}")

        # ── NAV-01: Home nav active state ────────────────────────
        driver.get(f"{BASE_URL}/")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-01", "Home nav active state", active == "HOME", f"Active: '{active}'")

        # Check orange border
        border_color = get_active_nav_style(driver)
        # Orange rgb is roughly (249, 115, 22) = rgba(249, 115, 22, 1)
        is_orange = border_color is not None and ("249" in border_color or "f97316" in border_color.lower())
        log("NAV-01b", "Home nav has orange border-left", is_orange, f"border-left-color: {border_color}")

        # ── NAV-02: Explore nav active state ─────────────────────
        driver.get(f"{BASE_URL}/explore")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-02", "Explore nav active state", active == "EXPLORE", f"Active: '{active}'")

        # ── NAV-03: Replies nav active state ─────────────────────
        driver.get(f"{BASE_URL}/replies")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-03", "Replies nav active state", active == "REPLIES", f"Active: '{active}'")

        # ── NAV-04: Profile nav active state ─────────────────────
        driver.get(f"{BASE_URL}/@{TEST_USER}")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-04", "Profile nav active state", active == "PROFILE", f"Active: '{active}'")

        # ── NAV-05: Settings nav active state ────────────────────
        driver.get(f"{BASE_URL}/settings")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-05", "Settings nav active state", active == "SETTINGS", f"Active: '{active}'")

        # ── NAV-06: Profile active on followers page ─────────────
        driver.get(f"{BASE_URL}/@{TEST_USER}/followers")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-06", "Profile active on followers page", active == "PROFILE", f"Active: '{active}'")

        # ── NAV-07: Profile active on following page ─────────────
        driver.get(f"{BASE_URL}/@{TEST_USER}/following")
        time.sleep(0.3)
        active = get_active_nav(driver)
        log("NAV-07", "Profile active on following page", active == "PROFILE", f"Active: '{active}'")

        # ── NAV-08: Only one nav active at a time ────────────────
        all_pass = True
        for path, expected in [("/", "HOME"), ("/explore", "EXPLORE"), ("/replies", "REPLIES"),
                               (f"/@{TEST_USER}", "PROFILE"), ("/settings", "SETTINGS")]:
            driver.get(f"{BASE_URL}{path}")
            time.sleep(0.3)
            count = count_active_navs(driver)
            if count != 1:
                all_pass = False
                break
        log("NAV-08", "Only one nav active at a time", all_pass, f"Last count: {count}")

        # ── NAV-11: Nav hover effect ─────────────────────────────
        driver.get(f"{BASE_URL}/")
        time.sleep(0.3)
        explore_nav = driver.find_element(By.XPATH, "//a[contains(@class,'nav-item')]/span[text()='EXPLORE']/..")
        original_color = explore_nav.value_of_css_property("color")
        # Use ActionChains for hover
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element(explore_nav).perform()
        time.sleep(0.3)
        hover_color = explore_nav.value_of_css_property("color")
        colors_changed = original_color != hover_color
        log("NAV-11", "Nav hover changes color", colors_changed,
            f"Before: {original_color}, After: {hover_color}")

        # ── NAV-12: Logout works ─────────────────────────────────
        driver.get(f"{BASE_URL}/logout")
        time.sleep(0.5)
        # Should redirect to register, nav should show logged-out state
        nav_labels = get_all_nav_labels(driver)
        logged_out = "LOGIN" in nav_labels and "LOGOUT" not in nav_labels
        log("NAV-12", "LOGOUT clears session and updates nav", logged_out, f"Nav after logout: {nav_labels}")

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
