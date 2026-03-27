"""
Frontend extensions for DIT.
Layers on top of wsgi.py — adds template helpers, enhanced views, and settings.
Run with:  python3 -m flask --app app:wib run
"""

import flask
from wsgi import wib, cnx, replchar, get_like, get_post, get_sub_posts, \
                 get_posts_by_username, get_followers, get_following, IntegrityError

# ── Template Filter: snowflake → username ──────────────────────────

_uname_cache = {}

@wib.template_filter('to_username')
def to_username_filter(owner):
    if not owner or owner == 0 or owner == 'anonymous':
        return 'anonymous'
    if isinstance(owner, str):
        return owner
    if owner in _uname_cache:
        return _uname_cache[owner]
    qu = cnx.cursor()
    qu.execute('SELECT username FROM users WHERE snowflake=%s'.replace('%s', replchar), (int(owner),))
    row = qu.fetchone()
    name = row[0] if row else 'unknown'
    _uname_cache[owner] = name
    return name


# ── Context Processor: helpers for every template ──────────────────

@wib.context_processor
def inject_helpers():
    def check_liked(post_sf):
        if 'snowflake' not in flask.session:
            return False
        return get_like(flask.session['snowflake'], post_sf)

    def get_likes(post_sf):
        qu = cnx.cursor()
        qu.execute('SELECT COUNT(*) FROM likes WHERE post=%s'.replace('%s', replchar), (post_sf,))
        return qu.fetchone()[0]

    def get_replies(post_sf):
        qu = cnx.cursor()
        qu.execute('SELECT COUNT(*) FROM posts WHERE reply_to=%s'.replace('%s', replchar), (post_sf,))
        return qu.fetchone()[0]

    return dict(check_liked=check_liked, get_likes=get_likes, get_replies=get_replies)


# ── Enhanced Views (replace wsgi.py view functions) ────────────────

def show_post_enhanced(username, post_id):
    """/@username/<post_id> — single post with replies + like data."""
    try:
        p = get_post(post_id)
    except StopIteration:
        return 'Post not found', 404
    replies = get_sub_posts(post_id)
    qu = cnx.cursor()
    qu.execute('SELECT COUNT(*) FROM likes WHERE post=%s'.replace('%s', replchar), (post_id,))
    like_count = qu.fetchone()[0]
    user_liked = False
    if 'snowflake' in flask.session:
        user_liked = get_like(flask.session['snowflake'], post_id)
    return flask.render_template('specific_post.html',
        post=p, replies=replies, like_count=like_count,
        user_liked=user_liked, username=flask.session.get('username', ''),
        userPFP=flask.session.get('PFP'))

wib.view_functions['show_post_pagehandle'] = show_post_enhanced


def user_profile_enhanced(username):
    """/@username — profile with follower counts + follow status."""
    qu = cnx.cursor()
    qu.execute('SELECT snowflake, username, displayname, PFP, bio FROM users WHERE username=%s'.replace('%s', replchar), (username,))
    user_info = None
    for row in qu:
        user_info = {'snowflake': row[0], 'username': row[1], 'displayname': row[2], 'PFP': row[3], 'bio': row[4]}
        break
    if not user_info:
        return flask.redirect(flask.url_for('index_pagehandle'))
    posts = get_posts_by_username(username)
    follower_count = len(get_followers(username))
    following_count = len(get_following(username))
    is_following = False
    if 'snowflake' in flask.session:
        qu2 = cnx.cursor()
        qu2.execute('SELECT 1 FROM follows WHERE follower=%s AND leader=%s'.replace('%s', replchar),
                    (flask.session['snowflake'], user_info['snowflake']))
        is_following = qu2.fetchone() is not None
    return flask.render_template('specific_user.html',
        posts=posts, user=user_info,
        follower_count=follower_count, following_count=following_count,
        is_following=is_following, username=flask.session.get('username', ''))

wib.view_functions['specific_user_pagehandle'] = user_profile_enhanced


# ── Settings Routes ────────────────────────────────────────────────

def _get_user(snowflake):
    qu = cnx.cursor()
    qu.execute('SELECT snowflake, username, displayname, PFP, bio FROM users WHERE snowflake=%s'.replace('%s', replchar), (snowflake,))
    row = qu.fetchone()
    if row:
        return {'snowflake': row[0], 'username': row[1], 'displayname': row[2] or row[1], 'PFP': row[3] or '', 'bio': row[4] or ''}
    return None

@wib.route('/settings')
def settings_page():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login_pagehandle'))
    return flask.render_template('settings.html', profile=_get_user(flask.session['snowflake']), username=flask.session['username'])

@wib.route('/settings/profile', methods=['POST'])
def update_profile():
    if 'snowflake' not in flask.session:
        return flask.redirect(flask.url_for('login_pagehandle'))
    qu = cnx.cursor()
    qu.execute('UPDATE users SET bio=%s, PFP=%s, displayname=%s WHERE snowflake=%s'.replace('%s', replchar),
               (flask.request.form.get('bio', ''), flask.request.form.get('pfp', ''),
                flask.request.form.get('displayname', ''), flask.session['snowflake']))
    cnx.commit()
    return flask.render_template('settings.html', profile=_get_user(flask.session['snowflake']),
                                 username=flask.session['username'], success='Profile updated.')

@wib.route('/settings/password', methods=['POST'])
def change_password():
    if 'snowflake' not in flask.session:
        return flask.redirect(flask.url_for('login_pagehandle'))
    cur_pw = flask.request.form.get('current_password', '')
    new_pw = flask.request.form.get('new_password', '')
    confirm = flask.request.form.get('confirm_password', '')
    def _err(msg):
        return flask.render_template('settings.html', profile=_get_user(flask.session['snowflake']),
                                     username=flask.session['username'], error=msg)
    if new_pw != confirm:
        return _err('New passwords do not match.')
    if not 6 <= len(new_pw) <= 128:
        return _err('Password must be between 6 and 128 characters.')
    qu = cnx.cursor()
    qu.execute('SELECT 1 FROM users WHERE snowflake=%s AND password=%s'.replace('%s', replchar),
               (flask.session['snowflake'], cur_pw.encode('UTF8').hex()))
    if not qu.fetchone():
        return _err('Current password is incorrect.')
    qu.execute('UPDATE users SET password=%s WHERE snowflake=%s'.replace('%s', replchar),
               (new_pw.encode('UTF8').hex(), flask.session['snowflake']))
    cnx.commit()
    return flask.render_template('settings.html', profile=_get_user(flask.session['snowflake']),
                                 username=flask.session['username'], success='Password changed successfully.')

# Flask auto-discovery
app = wib
