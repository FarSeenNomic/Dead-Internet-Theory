import flask
import time
import configparser

config = configparser.ConfigParser()
out = config.read('settings.ini')
DEBUG_MODE = len(out) == 0


if DEBUG_MODE:
  import sqlite3
  replchar = "?"
  OperationalError = sqlite3.OperationalError
  IntegrityError = sqlite3.IntegrityError
else:
  print(config['DEFAULT']['host'])
  import mysql.connector
  replchar = "%s"
  OperationalError = mysql.connector.errors.ProgrammingError
  IntegrityError = mysql.connector.errors.IntegrityError

def current_milli_time():
    return round(time.time() * 1000)

if DEBUG_MODE:
  cnx = sqlite3.connect(":memory:", check_same_thread=False)
else:
  cnx = mysql.connector.connect(
    host=config['DEFAULT']['host'],
    user=config['DEFAULT']['user'],
    password=config['DEFAULT']['password'],
    database=config['DEFAULT']['database'],
  )

wib = flask.Flask(__name__)
if DEBUG_MODE:
  wib.secret_key = str(current_milli_time())
else:
  wib.secret_key = config['DEFAULT']['secret']

cursor = cnx.cursor()

class post():
  def __init__(self, snowflake, owner, text, reply_to, image):
    self.snowflake = snowflake
    self.owner = owner
    self.owner_pfp = ""
    self.text = text
    self.reply_to = reply_to
    self.image = image
    self.comment_count = 0
    self.repost_count = 0
    self.like_count = 0

'''
try:
  cursor.execute("USE CLASS")
except mysql.connector.Error as err:
  cursor.execute("CREATE DATABASE CLASS DEFAULT CHARACTER SET 'utf8'")
  cursor.execute("USE CLASS")
  print("using class")
'''

urlrep = ("URL", "VARCHAR(1000) DEFAULT ''")

try:
  cursor.execute("""CREATE TABLE users (
  snowflake   BIGINT,
  username    VARCHAR(255),
  password    VARCHAR(255) NOT NULL,
  displayname VARCHAR(255),
  PFP         URL,
  bio         TINYTEXT,
  api_key     CHAR(64),
    UNIQUE (username),
    PRIMARY KEY (snowflake)
)""".replace(*urlrep))
  print("users table created.")
except OperationalError:
  print("users table exists.")

try:
  cursor.execute("""CREATE TABLE posts (
  snowflake       BIGINT,
  owner_snowflake BIGINT NOT NULL,
  text            VARCHAR(140),
  reply_to        BIGINT,  -- might be a top-level post
  image           URL,
    PRIMARY KEY (snowflake),
    CONSTRAINT FK_postOwner FOREIGN KEY (owner_snowflake) REFERENCES users(snowflake),
    CONSTRAINT FK_reply     FOREIGN KEY (reply_to)        REFERENCES posts(snowflake)
)""".replace(*urlrep))
  print("posts table created.")
except OperationalError:
  print("posts table exists.")

try:
  cursor.execute("""CREATE TABLE follows (
  follower      BIGINT,
  leader        BIGINT,
  snowflake     BIGINT,
    PRIMARY KEY (follower, leader),
    CONSTRAINT FK_follower      FOREIGN KEY (follower) REFERENCES users(snowflake),
    CONSTRAINT FK_follow_leader FOREIGN KEY (leader)   REFERENCES users(snowflake)
)""".replace(*urlrep))
  print("followers table created.")
except OperationalError:
  print("followers table exists.")

try:
  cursor.execute("""CREATE TABLE likes (
  follower      BIGINT,
  post          BIGINT,
    PRIMARY KEY (follower, post),
    CONSTRAINT FK_likeperson FOREIGN KEY (follower) REFERENCES users(snowflake),
    CONSTRAINT FK_likepost   FOREIGN KEY (post)     REFERENCES posts(snowflake)
)""".replace(*urlrep))
  print("likes table created.")
except OperationalError:
  print("likes table exists.")

# https://i.redd.it/maes48axh3re1.jpeg

def create_user(nam, pas):
  qu = cnx.cursor()
  time = current_milli_time()
  qu.execute("""
    INSERT INTO users
    (snowflake, username, password, displayname, PFP, bio)
    VALUES (%s, %s, %s, %s, %s, %s)""".replace("%s", replchar),
    (time, nam, pas.encode("UTF8").hex(), None, "/noPFP.jpg", "<ASL>? DTF.", )
  )
  return time

def get_posts(snowflake=0, *, include_counts=False):
  qu = cnx.cursor()
  if snowflake:
    qu.execute("SELECT * FROM posts WHERE reply_to=%s ORDER BY snowflake DESC LIMIT 255".replace("%s", replchar), (snowflake,))
  else:
    qu.execute("SELECT * FROM posts ORDER BY snowflake DESC LIMIT 255")
  postc = []
  for data in qu:
    postc.append(post(*data))
  if include_counts:
    for data in postc:
      data.comment_count = get_reply_count(data.snowflake)
      #data.repost_count = get_repost_count(data.snowflake)
      data.like_count = get_like_count(data.snowflake)
  return postc

def get_reply_count(snowflake):
  qu = cnx.cursor()
  qu.execute("SELECT COUNT(*) FROM posts WHERE reply_to=%s".replace("%s", replchar), (snowflake,))
  for data in qu:
    return data[0]
  return 0

def get_like_count(snowflake):
  qu = cnx.cursor()
  qu.execute("SELECT COUNT(*) FROM likes WHERE post=%s".replace("%s", replchar), (snowflake,))
  for data in qu:
    return data[0]
  return 0

def get_posts_by_username(username):
  qu = cnx.cursor()
  qu.execute("""SELECT p.snowflake, p.owner_snowflake, p.text, p.reply_to, p.image 
                FROM posts p JOIN users u ON p.owner_snowflake = u.snowflake 
                WHERE u.username=%s ORDER BY p.snowflake DESC LIMIT 255""".replace("%s", replchar), (username,))
  postc = []
  for data in qu:
    postc.append(post(*data))
  for data in postc:
    data.comment_count = get_reply_count(data.snowflake)
    #data.repost_count = get_repost_count(data.snowflake)
    data.like_count = get_like_count(data.snowflake)
  return postc

def make_post(owner, text, reply_to, image):
  qu = cnx.cursor()
  qu.execute("""
INSERT INTO posts
(snowflake, owner_snowflake, text, reply_to, image)
VALUES (%s, %s, %s, %s, %s)
""".replace("%s", replchar), (current_milli_time(), owner, text, reply_to, image, ))
  cnx.commit()
  return True

def like_post(follower, post):
  qu = cnx.cursor()
  qu.execute("INSERT INTO likes (follower, post) VALUES (%s, %s)".replace("%s", replchar), (follower, post, ))
  cnx.commit()
  return True

def unlike_post(follower, post):
  qu = cnx.cursor()
  qu.execute("DELETE FROM likes WHERE follower=%s AND post=%s".replace("%s", replchar), (follower, post, ))
  cnx.commit()
  return True

def follow_user(follower, leader):
  qu = cnx.cursor()
  qu.execute("INSERT INTO follows (follower, leader, snowflake) VALUES (%s, %s, %s)".replace("%s", replchar), (follower, leader, current_milli_time()))
  cnx.commit()
  return True

def unfollow_user(follower, leader):
  qu = cnx.cursor()
  qu.execute("DELETE FROM follows WHERE follower=%s AND leader=%s".replace("%s", replchar), (follower, leader, ))
  cnx.commit()
  return True

def get_followers(username):
  qu = cnx.cursor()
  qu.execute("""SELECT u.snowflake, u.username, u.displayname, u.PFP, u.bio 
                FROM users u JOIN follows f ON u.snowflake = f.follower 
                JOIN users target ON f.leader = target.snowflake 
                WHERE target.username=%s""".replace("%s", replchar), (username,))
  return [{"snowflake": r[0], "username": r[1], "displayname": r[2], "PFP": r[3], "bio": r[4]} for r in qu]

def get_following(username):
  qu = cnx.cursor()
  qu.execute("""SELECT u.snowflake, u.username, u.displayname, u.PFP, u.bio 
                FROM users u JOIN follows f ON u.snowflake = f.leader 
                JOIN users target ON f.follower = target.snowflake 
                WHERE target.username=%s""".replace("%s", replchar), (username,))
  return [{"snowflake": r[0], "username": r[1], "displayname": r[2], "PFP": r[3], "bio": r[4]} for r in qu]

def get_like(follower, post):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM likes WHERE follower=%s AND post=%s".replace("%s", replchar), (follower, post,))
  for i in qu:
    return True
  return False

def get_post(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE snowflake=%s LIMIT 1".replace("%s", replchar), (postnum,))
  return post(*next(qu))

def get_sub_posts(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to=%s ORDER BY snowflake".replace("%s", replchar), (postnum,)) # TODO: recurse?
  return [post(*data) for data in qu]

@wib.route("/")
def index_pagehandle():
  if 'username' in flask.session:
    return flask.render_template('homepage.html', posts=get_posts(include_counts=True), username=flask.session.get('username'))
  else:
    return flask.redirect(flask.url_for('register_pagehandle'))

@wib.route('/@<username>')
def specific_user_pagehandle(username):
  qu = cnx.cursor()
  qu.execute("SELECT snowflake, username, displayname, PFP, bio FROM users WHERE username=%s".replace("%s", replchar), (username,))
  user_info = None
  for row in qu:
    user_info = {
      "snowflake": row[0],
      "username": row[1],
      "displayname": row[2],
      "PFP": row[3],
      "bio": row[4]
    }
    break
  
  if not user_info:
    return flask.redirect(flask.url_for('index_pagehandle'))
    
  posts = get_posts_by_username(username)
  return flask.render_template('specific_user.html', posts=posts, user=user_info)

@wib.route('/@<username>/followers')
def followers_pagehandle(username):
  followers = get_followers(username)
  return flask.render_template('followers.html', followers=followers, username=username)

@wib.route('/@<username>/following')
def following_pagehandle(username):
  following = get_following(username)
  return flask.render_template('following.html', following=following, username=username)

@wib.route('/login', methods=['GET', 'POST'])
def login_pagehandle():
  if flask.request.method == 'GET':
    return flask.render_template('login.html')
  qu = cnx.cursor()

  username_try = flask.request.form.get('username')
  password_try = flask.request.form.get('password')

  # database verifies unique.
  username_try = username_try.strip()

  if username_try.startswith("@"):
    username_try = username_try[1:]

  qu.execute("SELECT snowflake, username FROM users WHERE USERNAME=%s AND PASSWORD=%s".replace("%s", replchar),
    (username_try, password_try.encode("UTF8").hex(), ))
  for snowflake, username in qu:
    flask.session['snowflake'] = snowflake
    flask.session['username'] = username
    return flask.redirect(flask.url_for('index_pagehandle'))
  return flask.render_template('login.html', error="Username and Password not found."), 401

@wib.route('/register', methods=['GET', 'POST'])
def register_pagehandle():
  if flask.request.method == 'GET':
    return flask.render_template('register.html')
  username_try = flask.request.form.get('username')
  password_try = flask.request.form.get('password')

  # database verifies unique.
  username_try = username_try.strip()

  if username_try.startswith("@"):
    username_try = username_try[1:]

  if not 6 <= len(password_try) <= 64:
    return flask.render_template('register.html', error="Password must be between 6 and 128 characters."), 422

  try:
    create_user(username_try, password_try)
  except IntegrityError:
    return flask.render_template('register.html', error="Username Taken."), 409

  return flask.redirect(flask.url_for('login_pagehandle'))

@wib.route('/logout')
def logout_pagehandle():
    # remove the username from the flask.session if it's there
    flask.session.pop('username', None)
    flask.session.pop('snowflake', None)
    return flask.redirect(flask.url_for('index_pagehandle'))

@wib.route('/create', methods=['GET', 'POST'])
def create_pagehandle():
  if flask.request.method == 'GET':
    return flask.redirect(flask.url_for('index_pagehandle'))

  owner = flask.session.get('snowflake')
  if not owner:
    return "Bad Info", 401

  make_post(owner, flask.request.form.get("text", ""), None, flask.request.form.get("image", ""))

  return flask.redirect(flask.url_for('index_pagehandle'))

@wib.route('/reply/<int:post_id>', methods=['GET', 'POST'])
def reply_pagehandle(post_id):
  if flask.request.method == 'GET':
    return flask.redirect(flask.url_for('index_pagehandle'))

  owner = flask.session.get('snowflake')
  if not owner:
    return "Bad Info", 401

  make_post(owner, flask.request.form.get("text", ""), post_id, flask.request.form.get("image", ""))

  return flask.redirect(flask.url_for('index_pagehandle'))

@wib.route('/@<username>/<int:post_id>')
def show_post_pagehandle(username, post_id):
  return flask.render_template('specific_post.html', post=get_post(post_id))

@wib.route('/reboot', methods=['GET', 'POST'])
def reboot_pagehandle():
  """
  Used for exiting the wsgi interface, allowing code to resume
  """
  if flask.request.method == 'POST':
    import hashlib, os, signal
    m = hashlib.md5()
    m.update(flask.request.form.get('REBOOTCODE').encode())
    if m.hexdigest().upper() == "3DA5DAC093EFA65422CBB22AF4588C65":
      os.kill(os.getpid(), signal.SIGINT)
  return '<form method="post"><p><input type=text name=REBOOTCODE><p><input type=submit value=REBOOT></form>'

# === API ===

@wib.route('/user.json/@<username>')
def user_apihandle(username):
  qu = cnx.cursor()
  qu.execute("""SELECT p.snowflake, p.owner_snowflake, p.text, p.reply_to, p.image 
                FROM posts p JOIN users u ON p.owner_snowflake = u.snowflake 
                WHERE u.username=%s ORDER BY p.snowflake DESC LIMIT 255""".replace("%s", replchar), (username,))
  posts = []
  for snowflake, owner_snowflake, text, reply_to, image in qu:
    posts.append({
      "snowflake": snowflake,
      "owner_snowflake": owner_snowflake,
      "text": text,
      "reply_to": reply_to,
      "image": image
    })
  return flask.jsonify(posts)

@wib.route('/post.json/<int:post_id>', methods=['POST'])
def post_apihandle(post_id):
  qu = cnx.cursor()
  qu.execute("SELECT snowflake, owner_snowflake, text, reply_to, image FROM posts WHERE snowflake=%s".replace("%s", replchar), (post_id) )
  for snowflake, owner_snowflake, text, reply_to, image in qu:
    return {"snowflake": snowflake, "owner_snowflake": owner_snowflake, "text": text, "reply_to": reply_to, "image": image}
  return {}

@wib.route('/like.json/<int:post_id>', methods=['POST'])
def like_apihandle(post_id):
  qu = cnx.cursor()
  try:
    snowflake = flask.session.get('snowflake')
    if not snowflake:
      return "Bad Info", 401
    like_post(snowflake, post_id)
    return flask.jsonify(True), 200
  except IntegrityError:
    return flask.jsonify(False), 409

@wib.route('/unlike.json/<int:post_id>', methods=['POST'])
def unlike_apihandle(post_id):
  qu = cnx.cursor()
  try:
    snowflake = flask.session.get('snowflake')
    if not snowflake:
      return "Bad Info", 401
    unlike_post(snowflake, post_id)
    return flask.jsonify(True), 200
  except IntegrityError:
    return flask.jsonify(False), 409

@wib.route('/follow.json/<int:leader_id>', methods=['POST'])
def follow_apihandle(leader_id):
  qu = cnx.cursor()
  try:
    snowflake = flask.session.get('snowflake')
    if not snowflake:
      return "Bad Info", 401
    follow_user(snowflake, leader_id)
    return flask.jsonify(True), 200
  except IntegrityError:
    return flask.jsonify(False), 409

@wib.route('/unfollow.json/<int:leader_id>', methods=['POST'])
def unfollow_apihandle(leader_id):
  qu = cnx.cursor()
  try:
    snowflake = flask.session.get('snowflake')
    if not snowflake:
      return "Bad Info", 401
    unfollow_user(snowflake, leader_id)
    return flask.jsonify(True), 200
  except IntegrityError:
    return flask.jsonify(False), 409
