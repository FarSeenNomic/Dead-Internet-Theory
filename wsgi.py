import flask
import time
import configparser

config = configparser.ConfigParser()
out = config.read('settings.ini')
DEBUG_MODE = len(out) == 0

if DEBUG_MODE:
  import sqlite3
  mysql = lambda _:_
  mysql.connector = mysql
  mysql.connector.errors = mysql
  mysql.connector.errors.ProgrammingError = sqlite3.OperationalError
  replchar = "?"
else:
  print(config['DEFAULT']['host'])
  import mysql.connector
  replchar = "%s"

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
  wib.secret_key = "BRILLIG"
else:
  wib.secret_key = config['DEFAULT']['secret']

cursor = cnx.cursor()

class post():
  def __init__(self, snowflake, owner, text, reply_to, image):
    self.snowflake = snowflake
    if owner:
      self.owner = owner
    else:
      self.owner = "anonymous"
    self.text = text
    self.reply_to = reply_to
    self.image = image

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
except mysql.connector.errors.ProgrammingError:
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
except mysql.connector.errors.ProgrammingError:
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
except mysql.connector.errors.ProgrammingError:
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
except mysql.connector.errors.ProgrammingError:
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

def get_posts():
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to IS NULL ORDER BY snowflake DESC LIMIT 15")
  return [post(*data) for data in qu]

def make_post(owner, text, reply_to, image):
  qu = cnx.cursor()
  qu.execute("""
INSERT INTO posts
(snowflake, owner_snowflake, text, reply_to, image)
VALUES (%s, %s, %s, %s, %s)
""".replace("%s", replchar), (current_milli_time(), owner, text, reply_to, image, ))
  cnx.commit()
  return True

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
    return flask.render_template('homepage.html', posts=get_posts(), username=flask.session['username'])
  else:
    return flask.redirect(flask.url_for('register_pagehandle'))

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
  return flask.render_template('login.html', error="Username and Password not found.")

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

  if not 6 <= len(password_try) <= 128:
    return flask.render_template('register.html', error="Password must be between 6 and 128 characters.")

  try:
    print( username_try, password_try.encode("UTF8").hex() )
    create_user(username_try, password_try)
  except sqlite3.IntegrityError:
    return flask.render_template('register.html', error="Username Taken.")

  return flask.redirect(flask.url_for('login_pagehandle'))

@wib.route('/logout')
def logout_pagehandle():
    # remove the username from the flask.session if it's there
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('index_pagehandle'))

@wib.route('/create', methods=['GET', 'POST'])
def create_pagehandle():
  if flask.request.method == 'GET':
    return flask.redirect(flask.url_for('index_pagehandle'))

  owner = flask.session['snowflake']
  if flask.request.form.get('anon'):
    owner = 0
  print(owner)

  make_post(owner, flask.request.form.get("text", ""), None, flask.request.form.get("image", ""))

  return flask.redirect(flask.url_for('index_pagehandle'))

@wib.route('/post/<int:post_id>')
def show_post_pagehandle(post_id):
  #assert typeof(post_id, int)
  return [get_post(post_id), get_sub_posts(post_id)]

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
