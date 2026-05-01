"""
TS-03: Post Cards — UI Unit Tests
Tests the feed post cards, like toggles, links, share functionality, and image attachments.
Uses Selenium WebDriver (Chrome) against a running DIT instance.

Usage:
    python3 testcases/ts03_post_cards.py [BASE_URL]
    Default BASE_URL: http://localhost:5000
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
TEST_USER = "cardtester_" + str(int(time.time()) % 100000)
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

def create_test_post(driver, text, image_url=None):
    """Creates a post to ensure there's at least one in the feed."""
    driver.get(f"{BASE_URL}/")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "composer-text")))
    driver.find_element(By.ID, "composer-text").send_keys(text)
    
    if image_url:
        driver.find_element(By.CSS_SELECTOR, ".tool-btn[title='Image URL']").click()
        time.sleep(0.2)
        driver.find_element(By.ID, "image-url-input").send_keys(image_url)
    
    driver.find_element(By.ID, "senddit-btn").click()
    time.sleep(1)

def main():
    print(f"\n{'='*60}")
    print(f"  TS-03: POST CARDS")
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
        
        # Create a basic post and an image post
        create_test_post(driver, f"Basic text post {int(time.time())}")
        create_test_post(driver, f"Image post {int(time.time())}", "https://ui-avatars.com/api/?name=CardTest&size=100")
        
        driver.get(f"{BASE_URL}/")
        time.sleep(1)
        
        # We need a reference to the top post
        try:
            post_card = driver.find_elements(By.CSS_SELECTOR, ".post-card")[0]
        except Exception as e:
            print("  [FATAL] No posts found to test against!")
            return 1

        # ─────────────────────────────────────────────────────────
        # PC-01: Post card renders all elements
        # ─────────────────────────────────────────────────────────
        try:
            has_avatar = len(post_card.find_elements(By.CSS_SELECTOR, ".post-avatar img")) > 0
            has_name = len(post_card.find_elements(By.CSS_SELECTOR, ".post-name")) > 0
            has_handle = len(post_card.find_elements(By.CSS_SELECTOR, ".post-handle")) > 0
            has_view = len(post_card.find_elements(By.CSS_SELECTOR, ".post-time")) > 0
            has_text = len(post_card.find_elements(By.CSS_SELECTOR, ".post-text")) > 0
            has_actions = len(post_card.find_elements(By.CSS_SELECTOR, ".post-actions .action-item")) >= 3
            
            all_elements = has_avatar and has_name and has_handle and has_view and has_text and has_actions
            log("PC-01", "Post card renders all elements", all_elements, 
                f"avatar:{has_avatar}, name:{has_name}, handle:{has_handle}, view:{has_view}, actions:{has_actions}")
        except Exception as e:
            log("PC-01", "Post card renders all elements", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-02: Avatar links to profile
        # ─────────────────────────────────────────────────────────
        try:
            avatar_link = post_card.find_element(By.CSS_SELECTOR, ".post-avatar a").get_attribute("href")
            log("PC-02", "Avatar links to profile", f"/@{TEST_USER}" in avatar_link, f"href: {avatar_link}")
        except Exception as e:
            log("PC-02", "Avatar links to profile", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-03: Display name links to profile
        # ─────────────────────────────────────────────────────────
        try:
            name_link = post_card.find_element(By.CSS_SELECTOR, ".post-name-link").get_attribute("href")
            log("PC-03", "Display name links to profile", f"/@{TEST_USER}" in name_link, f"href: {name_link}")
        except Exception as e:
            log("PC-03", "Display name links to profile", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-04: Post text links to detail
        # ─────────────────────────────────────────────────────────
        try:
            text_link = post_card.find_element(By.CSS_SELECTOR, "a:has(> .post-text)").get_attribute("href")
            # Should be /@username/snowflake
            parts = text_link.split(f"/@{TEST_USER}/")
            valid_link = len(parts) == 2 and parts[1].isdigit()
            log("PC-04", "Post text links to detail", valid_link, f"href: {text_link}")
        except Exception as e:
            log("PC-04", "Post text links to detail", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-05: Avatar fallback on broken PFP
        # ─────────────────────────────────────────────────────────
        try:
            avatar_img = post_card.find_element(By.CSS_SELECTOR, ".post-avatar img")
            has_onerror = avatar_img.get_attribute("onerror")
            log("PC-05", "Avatar fallback on broken PFP (onerror)", 
                has_onerror is not None and "ui-avatars" in has_onerror, 
                f"onerror={'present' if has_onerror else 'MISSING'}")
        except Exception as e:
            log("PC-05", "Avatar fallback on broken PFP", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-06: Image post displays attachment
        # ─────────────────────────────────────────────────────────
        try:
            # We know the first post has an image because we created it last
            image = post_card.find_element(By.CSS_SELECTOR, ".post-media img")
            is_displayed = image.is_displayed()
            src = image.get_attribute("src")
            log("PC-06", "Image post displays attachment", is_displayed, f"src: {src[:60]}...")
        except Exception as e:
            log("PC-06", "Image post displays attachment", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-07: Reply indicator shown
        # ─────────────────────────────────────────────────────────
        # Create a reply to the post we just found
        try:
            snowflake = post_card.find_element(By.CSS_SELECTOR, "a:has(> .post-text)").get_attribute("href").split("/")[-1]
            driver.get(f"{BASE_URL}/@{TEST_USER}/{snowflake}")
            time.sleep(1)
            driver.find_element(By.NAME, "text").send_keys("This is a reply")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(1)
            
            # Go back to feed to see the reply
            driver.get(f"{BASE_URL}/")
            time.sleep(1)
            new_top_post = driver.find_elements(By.CSS_SELECTOR, ".post-card")[0]
            reply_indicator = new_top_post.find_elements(By.CSS_SELECTOR, ".post-replying-to")
            
            has_indicator = len(reply_indicator) > 0 and f"#{snowflake}" in reply_indicator[0].text
            log("PC-07", "Reply indicator shown", has_indicator, 
                f"indicator text: {reply_indicator[0].text if has_indicator else 'None'}")
        except Exception as e:
            log("PC-07", "Reply indicator shown", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-08: Like toggle (unlike → like)
        # ─────────────────────────────────────────────────────────
        try:
            driver.get(f"{BASE_URL}/")
            time.sleep(1)
            post_card = driver.find_elements(By.CSS_SELECTOR, ".post-card")[0]
            like_container = post_card.find_element(By.XPATH, ".//*[contains(@class, 'like-toggle-')]")
            like_btn = like_container.find_element(By.TAG_NAME, "button")
            like_count_span = like_container.find_element(By.CSS_SELECTOR, ".action-count")
            
            initial_count = int(like_count_span.text.strip())
            initial_classes = like_container.get_attribute("class")
            
            if "active-orange" in initial_classes:
                # Need to unlike it first
                like_btn.click()
                time.sleep(0.5)
                initial_count -= 1
            
            # Now like it
            like_btn.click()
            time.sleep(0.5)
            
            new_classes = like_container.get_attribute("class")
            new_count = int(like_count_span.text.strip())
            
            success = "active-orange" in new_classes and new_count == initial_count + 1
            log("PC-08", "Like toggle (unlike → like)", success, 
                f"classes: {new_classes}, count: {initial_count} → {new_count}")
        except Exception as e:
            log("PC-08", "Like toggle (unlike → like)", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-09: Like toggle (like → unlike)
        # ─────────────────────────────────────────────────────────
        try:
            # It's currently liked from previous step
            like_btn.click()
            time.sleep(0.5)
            
            new_classes = like_container.get_attribute("class")
            new_count = int(like_count_span.text.strip())
            
            success = "active-orange" not in new_classes and new_count == initial_count
            log("PC-09", "Like toggle (like → unlike)", success, 
                f"classes: {new_classes}, count: {new_count}")
        except Exception as e:
            log("PC-09", "Like toggle (like → unlike)", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-10: Reply count displayed
        # ─────────────────────────────────────────────────────────
        try:
            # We replied to the SECOND post earlier (snowflake)
            # Find the post with that snowflake
            post_link = f"/@{TEST_USER}/{snowflake}"
            parent_post = driver.find_element(By.CSS_SELECTOR, f"a[href='{post_link}']:has(.post-text)").find_element(By.XPATH, "./ancestor::article")
            
            reply_action = parent_post.find_elements(By.CSS_SELECTOR, ".action-item")[0]
            reply_count = reply_action.find_element(By.CSS_SELECTOR, ".action-count").text.strip()
            
            log("PC-10", "Reply count displayed", reply_count == "1", f"count = {reply_count}")
        except Exception as e:
            log("PC-10", "Reply count displayed", False, str(e)[:80])

        # ─────────────────────────────────────────────────────────
        # PC-11: Share button copies link
        # ─────────────────────────────────────────────────────────
        try:
            post_card = driver.find_elements(By.CSS_SELECTOR, ".post-card")[0]
            share_btn = post_card.find_elements(By.CSS_SELECTOR, ".action-item")[-1].find_element(By.TAG_NAME, "button")
            
            # Click it
            share_btn.click()
            time.sleep(0.2)
            
            # Check for toast
            toasts = driver.find_elements(By.CSS_SELECTOR, ".copy-toast")
            has_toast = len(toasts) > 0 and "COPIED" in toasts[0].text
            log("PC-11", "Share button shows toast", has_toast, f"NOT DEPLOYED — {len(toasts)} toasts found" if not has_toast else "Toast visible")
        except Exception as e:
            log("PC-11", "Share button shows toast", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # PC-12: Share toast auto-dismisses
        # ─────────────────────────────────────────────────────────
        try:
            time.sleep(2.5) # Wait for dismissal
            toasts = driver.find_elements(By.CSS_SELECTOR, ".copy-toast")
            log("PC-12", "Share toast auto-dismisses", len(toasts) == 0, f"NOT DEPLOYED" if len(toasts)>0 else "Dismissed")
        except Exception as e:
            log("PC-12", "Share toast auto-dismisses", False, f"NOT DEPLOYED — {str(e)[:60]}")

        # ─────────────────────────────────────────────────────────
        # PC-13: Post card hover state
        # ─────────────────────────────────────────────────────────
        try:
            post_card = driver.find_elements(By.CSS_SELECTOR, ".post-card")[0]
            original_bg = post_card.value_of_css_property("background-color")
            
            ActionChains(driver).move_to_element(post_card).perform()
            time.sleep(0.3)
            
            hover_bg = post_card.value_of_css_property("background-color")
            changed = original_bg != hover_bg
            
            log("PC-13", "Post card hover state", changed, f"bg changed from {original_bg} to {hover_bg}")
        except Exception as e:
            log("PC-13", "Post card hover state", False, str(e)[:80])

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
