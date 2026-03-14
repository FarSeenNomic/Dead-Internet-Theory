import sqlite3
import flask
import time
import os

def current_milli_time():
    return round(time.time() * 1000)

# Connect to a local SQLite database instead of MySQL
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dit.db')
cnx = sqlite3.connect(db_path, check_same_thread=False)

wib = flask.Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
wib.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

# Setup SQLite Database Tables
try:
  cursor.execute("""CREATE TABLE users (
  snowflake   INTEGER PRIMARY KEY,
  username    VARCHAR(255) UNIQUE,
  password    VARCHAR(255) NOT NULL,
  displayname VARCHAR(255),
  PFP         TEXT DEFAULT '',
  bio         TEXT,
  api_key     CHAR(64) NOT NULL
)""")
  cnx.commit()
except sqlite3.Error:
  pass

try:
  cursor.execute("""CREATE TABLE posts (
  snowflake     INTEGER PRIMARY KEY,
  owner         VARCHAR(255) NOT NULL,
  text          TEXT,
  reply_to      INTEGER,
  image         TEXT DEFAULT ''
)""")
  cnx.commit()
except sqlite3.Error:
  pass

def get_posts():
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to IS NULL ORDER BY snowflake DESC LIMIT 15")
  return [post(*data) for data in qu.fetchall()]

def make_post(owner, text, reply_to, image):
  qu = cnx.cursor()
  qu.execute("""
INSERT INTO posts
(snowflake, owner, text, reply_to, image)
VALUES (?, ?, ?, ?, ?)
""", (current_milli_time(), owner, text, reply_to, image))
  cnx.commit()
  return True

def get_post(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE snowflake=? LIMIT 1", (postnum,))
  data = qu.fetchone()
  if data:
      return post(*data)
  return None

def get_sub_posts(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to=? ORDER BY snowflake", (postnum,))
  return [post(*data) for data in qu.fetchall()]

@wib.route("/")
def index():
  if 'username' in flask.session:
    return flask.render_template('homepage.html', posts=get_posts(), username=flask.session['username'])
  else:
    return '<meta http-equiv="refresh" content="0; url=/login" />'

@wib.route('/login', methods=['GET', 'POST'])
def login():
  # Simple login system for demo
  if flask.request.method == 'POST':
    flask.session['username'] = flask.request.form['username']
    return flask.redirect(flask.url_for('index'))
  return flask.render_template('login.html')

@wib.route('/logout')
def logout():
    # remove the username from the flask.session if it's there
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('index'))

@wib.route('/create', methods=['GET', 'POST'])
def create_post_route():
  if flask.request.method == 'GET':
    return flask.redirect(flask.url_for('index'))

  owner = flask.session.get('username', 'anonymous')
  if flask.request.form.get('anon'):
    owner = "anonymous"

  text = flask.request.form.get("text", "")
  image = flask.request.form.get("image", "")

  make_post(owner, text, None, image)
  return flask.redirect(flask.url_for('index'))

@wib.route('/post/<int:post_id>')
def show_post(post_id):
  return {"post": get_post(post_id), "replies": get_sub_posts(post_id)}
