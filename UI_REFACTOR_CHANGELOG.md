# Dead-Internet-Theory UI Refactor Changelog

## Overview
This branch completes a comprehensive UI/UX refactoring of the Dead-Internet-Theory frontend. The objective was to elevate the raw group-project template into a production-ready, brutalist-styled application. We focused purely on Jinja templates, CSS, and Vanilla JS, minimizing backend (`wsgi.py`) changes to strictly 5 lines to support frontend logic. 

Furthermore, we introduced a 67-case automated UI test suite using Selenium to validate all frontend interactions and prevent regressions.

---

## What's New

### 🧭 Navigation & Routing (`base.html`, `wsgi.py`)
- **Fix**: Resolved the "infinite redirect loop" bug by conditionally rendering the sidebar. Unauthenticated users now only see `HOME`, `EXPLORE`, `LOGIN`, and `REGISTER`.
- **Fix**: Corrected the sidebar "Active State" highlighting. Sub-pages (like `/followers` and `/following`) now properly highlight their parent section (PROFILE).
- **Feature**: Created a dedicated `templates/replies.html` template. The `/replies` route now points to this file, removing the confusing Post Composer box that used to appear at the top of the Replies feed.

### ✍️ Post Composer (`homepage.html`, `static/styles.css`)
- **Feature**: Added a live, dynamic 140-character counter. It drops to orange (`warn`) at 20 characters remaining and turns red (`over`) when the limit is exceeded.
- **Fix**: Added the missing `enctype="multipart/form-data"` to the composer form, which was previously silently dropping uploaded image files.
- **UX Polish**: Added a bouncing tooltip validation ("PLEASE FILL OUT THIS FIELD") that prevents users from submitting an empty post and auto-dismisses after 3 seconds.

### 💬 Social Actions & Post Cards (All Templates)
- **Feature**: Fully wired up the "Share" button (`data-lucide="share-2"`) to automatically copy the post's permalink to the user's clipboard.
- **UX Polish**: Designed and implemented a brutalist-themed "LINK COPIED" toast notification that appears upon successful share and auto-dismisses.
- **Fix**: Implemented a universal `onerror` fallback for all avatars. If a profile picture URL is broken or missing, it seamlessly falls back to a dynamically generated `ui-avatars.com` placeholder showing the user's name.

### ⚙️ Settings & Authentication (`settings.html`, `register.html`)
- **Fix**: Corrected the `<title>` tag on `register.html` so it no longer incorrectly says "Login - DIT".
- **Fix**: Added a 3-line check in `wsgi.py` so that if a user clears their custom PFP URL and hits save, the backend safely reverts them to the default Gravatar.
- **UX Polish**: Improved the Profile Picture preview logic in the settings menu, creating separate visual previews for when a user pastes a URL versus uploading a local file.

### 🧪 Automated Testing Infrastructure (`/testcases`)
- **Feature**: Built a fully functional Python/Selenium automated test suite covering 67 individual UI behaviors.
- **Suites Included**:
  - `TS-01`: Sidebar Navigation (Active states, auth rendering, hover effects)
  - `TS-02`: Post Composer (Character limits, tooltip validation, AJAX injection)
  - `TS-03`: Post Cards (Avatar fallbacks, like toggles, share links)
  - `TS-04`: Authentication (Form rendering, redirect paths)
  - `TS-05`: Settings (PFP Previews, form logic)
  - `TS-06`: Profile Page (Follow/Unfollow AJAX toggles)
- **Feature**: Added `run_all_tests.sh` to allow developers to run the entire suite locally.

---

## Files Modified
*   `wsgi.py` (+4 additions, 1 deletion)
*   `static/styles.css`
*   `templates/base.html`
*   `templates/followers.html`
*   `templates/following.html`
*   `templates/homepage.html`
*   `templates/register.html`
*   `templates/settings.html`
*   `templates/specific_post.html`
*   `templates/specific_user.html`

## Files Added
*   `templates/replies.html`
*   `UI_REFACTOR_CHANGELOG.md`
*   `testcases/ts01_sidebar_navigation.py`
*   `testcases/ts02_post_composer.py`
*   `testcases/ts03_post_cards.py`
*   `testcases/ts04_authentication.py`
*   `testcases/ts05_settings.py`
*   `testcases/ts06_profile.py`
*   `run_all_tests.sh`
