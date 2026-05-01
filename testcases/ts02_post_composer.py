"""
TS-02: Post Composer — UI Unit Tests
Tests the composer textarea, character counter, image handling,
validation tooltip, AJAX submission, and post card injection.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts02_post_composer.py [BASE_URL]
    Default BASE_URL: http://localhost:5000
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
TEST_USER = "cmptester_" + str(int(time.time()) % 100000)
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


def go_home(driver):
    """Navigate to homepage and wait for composer to load."""
    driver.get(f"{BASE_URL}/")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "composer-text"))
    )
    time.sleep(0.3)


def main():
    print(f"\n{'='*60}")
    print(f"  TS-02: POST COMPOSER")
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
        setup_user(driver)
        go_home(driver)

        # ─────────────────────────────────────────────────────────
        # CMP-01: Empty submit shows tooltip
        # ─────────────────────────────────────────────────────────
        try:
            textarea = driver.find_element(By.ID, "composer-text")
            textarea.clear()
            btn = driver.find_element(By.ID, "senddit-btn")
            btn.click()
            time.sleep(0.5)

            tooltip = driver.find_element(By.ID, "custom-tooltip")
            tooltip_visible = tooltip.is_displayed()
            tooltip_text = tooltip.text.strip()
            log("CMP-01", "Empty submit shows tooltip",
                tooltip_visible and "FILL" in tooltip_text,
                f"visible={tooltip_visible}, text='{tooltip_text}'")
        except Exception as e:
            log("CMP-01", "Empty submit shows tooltip", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-02: Tooltip auto-dismisses after 3 seconds
        # ─────────────────────────────────────────────────────────
        try:
            time.sleep(3.5)
            tooltip = driver.find_element(By.ID, "custom-tooltip")
            tooltip_gone = not tooltip.is_displayed()
            log("CMP-02", "Tooltip auto-dismisses after 3s", tooltip_gone,
                f"still visible={not tooltip_gone}")
        except Exception as e:
            log("CMP-02", "Tooltip auto-dismisses after 3s", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-03: Character counter starts at 140
        # ─────────────────────────────────────────────────────────
        try:
            go_home(driver)
            counter = driver.find_element(By.ID, "char-counter")
            counter_text = counter.text.strip()
            log("CMP-03", "Character counter starts at 140",
                counter_text == "140",
                f"Got: '{counter_text}'")
        except Exception as e:
            log("CMP-03", "Character counter starts at 140", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # CMP-04: Counter decrements on input
        # ─────────────────────────────────────────────────────────
        try:
            textarea = driver.find_element(By.ID, "composer-text")
            textarea.clear()
            textarea.send_keys("hello")
            time.sleep(0.3)
            counter = driver.find_element(By.ID, "char-counter")
            counter_text = counter.text.strip()
            log("CMP-04", "Counter decrements on input (5 chars → 135)",
                counter_text == "135",
                f"Got: '{counter_text}'")
        except Exception as e:
            log("CMP-04", "Counter decrements on input", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # CMP-05: Counter turns orange at ≤20
        # ─────────────────────────────────────────────────────────
        try:
            textarea = driver.find_element(By.ID, "composer-text")
            textarea.clear()
            time.sleep(0.1)
            textarea.send_keys("a" * 121)
            time.sleep(0.3)
            counter = driver.find_element(By.ID, "char-counter")
            counter_text = counter.text.strip()
            counter_classes = counter.get_attribute("class")
            log("CMP-05", "Counter turns orange at ≤20 remaining",
                counter_text == "19" and "warn" in counter_classes,
                f"text='{counter_text}', class='{counter_classes}'")
        except Exception as e:
            log("CMP-05", "Counter turns orange at ≤20", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # CMP-06: Counter turns red when over limit
        # ─────────────────────────────────────────────────────────
        try:
            textarea = driver.find_element(By.ID, "composer-text")
            textarea.clear()
            time.sleep(0.1)
            textarea.send_keys("x" * 141)
            time.sleep(0.3)
            counter = driver.find_element(By.ID, "char-counter")
            counter_text = counter.text.strip()
            counter_classes = counter.get_attribute("class")
            log("CMP-06", "Counter turns red when over 140",
                counter_text == "-1" and "over" in counter_classes,
                f"text='{counter_text}', class='{counter_classes}'")
        except Exception as e:
            log("CMP-06", "Counter turns red when over 140", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # CMP-07: Image URL toggle
        # ─────────────────────────────────────────────────────────
        try:
            go_home(driver)
            url_input = driver.find_element(By.ID, "image-url-input")
            initial_display = url_input.value_of_css_property("display")
            link_btn = driver.find_element(By.CSS_SELECTOR, ".tool-btn[title='Image URL']")
            link_btn.click()
            time.sleep(0.3)
            after_display = url_input.value_of_css_property("display")
            link_btn.click()
            time.sleep(0.3)
            toggled_back = url_input.value_of_css_property("display")
            log("CMP-07", "Image URL toggle shows/hides field",
                initial_display == "none" and after_display != "none" and toggled_back == "none",
                f"initial={initial_display}, after={after_display}, back={toggled_back}")
        except Exception as e:
            log("CMP-07", "Image URL toggle shows/hides field", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-08: Image URL preview
        # ─────────────────────────────────────────────────────────
        try:
            link_btn = driver.find_element(By.CSS_SELECTOR, ".tool-btn[title='Image URL']")
            link_btn.click()
            time.sleep(0.2)
            url_input = driver.find_element(By.ID, "image-url-input")
            url_input.clear()
            url_input.send_keys("https://ui-avatars.com/api/?name=TestImage&size=200")
            driver.execute_script(
                "document.getElementById('image-url-input').dispatchEvent(new Event('input'));"
            )
            time.sleep(0.5)
            preview_container = driver.find_element(By.ID, "image-preview-container")
            preview_visible = preview_container.is_displayed()
            preview_src = driver.find_element(By.ID, "image-preview").get_attribute("src")
            log("CMP-08", "Image URL preview shows image",
                preview_visible and "TestImage" in preview_src,
                f"visible={preview_visible}, src='{preview_src[:60]}...'")
        except Exception as e:
            log("CMP-08", "Image URL preview shows image", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-09: File upload input exists
        # ─────────────────────────────────────────────────────────
        try:
            go_home(driver)
            file_input = driver.find_element(By.ID, "image-file-input")
            accept_attr = file_input.get_attribute("accept")
            is_hidden = file_input.value_of_css_property("display") == "none"
            log("CMP-09", "File upload input exists, hidden, accepts image/*",
                is_hidden and accept_attr == "image/*",
                f"display={file_input.value_of_css_property('display')}, accept='{accept_attr}'")
        except Exception as e:
            log("CMP-09", "File upload input exists", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-10: Clear image preview
        # ─────────────────────────────────────────────────────────
        try:
            # Set up a preview first
            link_btn = driver.find_element(By.CSS_SELECTOR, ".tool-btn[title='Image URL']")
            link_btn.click()
            time.sleep(0.2)
            url_input = driver.find_element(By.ID, "image-url-input")
            url_input.clear()
            url_input.send_keys("https://ui-avatars.com/api/?name=ClearTest&size=200")
            driver.execute_script(
                "document.getElementById('image-url-input').dispatchEvent(new Event('input'));"
            )
            time.sleep(0.5)
            clear_btn = driver.find_element(By.CSS_SELECTOR, "#image-preview-container button")
            clear_btn.click()
            time.sleep(0.3)
            preview_container = driver.find_element(By.ID, "image-preview-container")
            preview_hidden = not preview_container.is_displayed()
            log("CMP-10", "Clear image preview hides container",
                preview_hidden,
                f"still visible={not preview_hidden}")
        except Exception as e:
            log("CMP-10", "Clear image preview hides container", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-11: AJAX post creation
        # ─────────────────────────────────────────────────────────
        try:
            go_home(driver)
            textarea = driver.find_element(By.ID, "composer-text")
            test_text = f"Selenium test {int(time.time())}"
            textarea.send_keys(test_text)
            time.sleep(0.2)

            btn = driver.find_element(By.ID, "senddit-btn")
            btn.click()
            time.sleep(2)

            textarea_val = textarea.get_attribute("value")
            textarea_cleared = textarea_val == ""
            post_in_dom = test_text in driver.page_source

            log("CMP-11", "AJAX post creation (card appears, textarea clears)",
                textarea_cleared and post_in_dom,
                f"cleared={textarea_cleared}, in_dom={post_in_dom}")
        except Exception as e:
            log("CMP-11", "AJAX post creation", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-12: Empty state removal
        # ─────────────────────────────────────────────────────────
        try:
            empty_states = driver.find_elements(By.CSS_SELECTOR, ".empty-state")
            visible_empties = [e for e in empty_states if e.is_displayed()]
            log("CMP-12", "Empty state removed after first post",
                len(visible_empties) == 0,
                f"visible empty states: {len(visible_empties)}")
        except Exception as e:
            log("CMP-12", "Empty state removed after first post", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-13: Composer avatar fallback
        # ─────────────────────────────────────────────────────────
        try:
            go_home(driver)
            composer_img = driver.find_element(By.CSS_SELECTOR, ".composer-avatar img")
            has_onerror = composer_img.get_attribute("onerror")
            log("CMP-13", "Composer avatar has onerror fallback",
                has_onerror is not None and "ui-avatars" in has_onerror,
                f"onerror={'present' if has_onerror else 'MISSING'}")
        except Exception as e:
            log("CMP-13", "Composer avatar has onerror fallback", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # CMP-14: Counter resets after post
        # ─────────────────────────────────────────────────────────
        try:
            counter = driver.find_element(By.ID, "char-counter")
            counter_after = counter.text.strip()
            log("CMP-14", "Counter resets to 140 after post submission",
                counter_after == "140",
                f"Got: '{counter_after}'")
        except Exception as e:
            log("CMP-14", "Counter resets to 140 after post", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # CMP-15: No composer on Replies page
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/replies")
            time.sleep(0.5)
            composers = driver.find_elements(By.CSS_SELECTOR, ".composer-section")
            no_composer = len(composers) == 0
            log("CMP-15", "No composer on Replies page",
                no_composer,
                f"composers found: {len(composers)}")
        except Exception as e:
            log("CMP-15", "No composer on Replies page", False, str(e)[:80])

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
