import mysql.connector
import flask
import time

def current_milli_time():
    return round(time.time() * 1000)

cnx = mysql.connector.connect(
  host="localhost",
  user="server",
  password="234890646",
  database='CLASS',
)

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

'''
try:
  cursor.execute("USE CLASS")
except mysql.connector.Error as err:
  cursor.execute("CREATE DATABASE CLASS DEFAULT CHARACTER SET 'utf8'")
  cursor.execute("USE CLASS")
  print("using class")
'''

urlrep = ("URL", "VARCHAR(200) DEFAULT ''")

try:
  cursor.execute("""CREATE TABLE users (
  snowflake   BIGINT,
  username    VARCHAR(255),
  password    VARCHAR(255) NOT NULL,
  displayname VARCHAR(255),
  PFP         URL,
  bio         TINYTEXT,
  api_key     CHAR(64) NOT NULL,
    UNIQUE (username),
    PRIMARY KEY (snowflake)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("users table good.")

try:
  cursor.execute("""CREATE TABLE posts (
  snowflake     BIGINT,
  owner         VARCHAR(255) NOT NULL,
  text          TEXT, -- TEXT means not null
  reply_to      BIGINT,  -- might be a top-level post
  image         URL,
    PRIMARY KEY (snowflake),
    CONSTRAINT FK_reply     FOREIGN KEY (reply_to) REFERENCES posts(snowflake)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("posts table good.")

try:
  cursor.execute("""CREATE TABLE follows (
  follower      VARCHAR(255),
  leader        VARCHAR(255),
  snowflake     BIGINT,
    PRIMARY KEY (follower, leader),
    CONSTRAINT FK_follower      FOREIGN KEY (follower) REFERENCES users(username),
    CONSTRAINT FK_follow_leader FOREIGN KEY (leader)   REFERENCES users(username)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("followers table good.")

try:
  cursor.execute("""CREATE TABLE likes (
  follower      VARCHAR(255),
  post          BIGINT,
    PRIMARY KEY (follower, post),
    CONSTRAINT FK_likeperson FOREIGN KEY (follower) REFERENCES users(username),
    CONSTRAINT FK_likepost   FOREIGN KEY (post)     REFERENCES posts(snowflake)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("likes table good.")


# https://i.redd.it/maes48axh3re1.jpeg
'''
cursor.execute("""
INSERT INTO users
(snowflake, username, password, displayname, PFP, bio)
VALUES (%s, %s, %s, %s, %s, %s)""",
("1", "my_name", "password", None, "http://example.com/", "<ASL>?", )
)
'''

# TODO: Seperate API calls from UI calls.
# keep it restfull

def get_posts():
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to IS NULL ORDER BY snowflake DESC LIMIT 15")
  return [post(*data) for data in qu.fetchall()]

def make_post(owner, text, reply_to, image):
  qu = cnx.cursor()
  qu.execute("""
INSERT INTO posts
(snowflake, owner, text, reply_to, image)
VALUES (%s, %s, %s, %s, %s)
""", (current_milli_time(), owner, text, reply_to, image, ))
  cnx.commit()
  return True

def get_post(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE snowflake=%s LIMIT 1", (postnum,))
  data = qu.fetchone()
  if data:
      return post(*data)
  return None

def get_sub_posts(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to=%s ORDER BY snowflake", (postnum,)) # TODO: recurse?
  return [post(*data) for data in qu.fetchall()]

@wib.route("/")
def index():
  if 'username' in flask.session:
    return flask.render_template('homepage.html', posts=get_posts(), username=flask.session['username'])
  else:
    return '<a href="/login">You are not logged in</a>'

@wib.route('/login', methods=['GET', 'POST'])
def login():
  # TODO: this is not a login system
  # Doesn't even verify if the username is correct
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
  return {"post": get_post(post_id).__dict__ if get_post(post_id) else None, "replies": [p.__dict__ for p in get_sub_posts(post_id)]}
