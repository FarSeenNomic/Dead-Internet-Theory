import mysql.connector
import flask
import time
import configparser

def current_milli_time():
    return round(time.time() * 1000)

config = configparser.ConfigParser()
config.read('example.ini')

if 'DEFAULT' not in config:
  print("config not found")
  exit()

cnx = mysql.connector.connect(
  host=config['DEFAULT']['host'],
  user=config['DEFAULT']['user'],
  password=config['DEFAULT']['password'],
  database=config['DEFAULT']['database'],
)

wib = flask.Flask(__name__)
wib.secret_key = config['DEFAULT']['sercret']

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
  snowflake   INT,
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
  snowflake     INT,
  owner         INT NOT NULL,
  text          TEXT, -- TEXT means not null
  reply_to      INT,  -- might be a top-level post
  image         URL,
    PRIMARY KEY (snowflake),
    CONSTRAINT FK_postOwner FOREIGN KEY (owner)    REFERENCES users(snowflake),
    CONSTRAINT FK_reply     FOREIGN KEY (reply_to) REFERENCES posts(snowflake)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("posts table good.")

try:
  cursor.execute("""CREATE TABLE follows (
  follower      INT,
  leader        INT,
  snowflake     INT,
    PRIMARY KEY (follower, leader),
    CONSTRAINT FK_follower      FOREIGN KEY (follower) REFERENCES users(snowflake),
    CONSTRAINT FK_follow_leader FOREIGN KEY (leader)   REFERENCES users(snowflake)
)""".replace(*urlrep))
except mysql.connector.errors.ProgrammingError:
  print("followers table good.")

try:
  cursor.execute("""CREATE TABLE likes (
  follower      INT,
  post          INT,
    PRIMARY KEY (follower, post),
    CONSTRAINT FK_likeperson FOREIGN KEY (follower) REFERENCES users(snowflake),
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
  return [post(*data) for data in qu]

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
  qu.execute("SELECT * FROM posts WHERE snowflake=% LIMIT 1", (postnum,))
  return post(*next(qu))

def get_sub_posts(postnum):
  qu = cnx.cursor()
  qu.execute("SELECT * FROM posts WHERE reply_to=% ORDER BY snowflake", (postnum,)) # TODO: recurse?
  return [post(*data) for data in qu]

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

_db_make_post = make_post

@wib.route('/create', methods=['GET', 'POST'])
def make_post():
  if flask.request.method == 'GET':
    return flask.redirect(flask.url_for('index'))

  owner = flask.session['username']
  if flask.request.form.get('anon'):
    owner = "anonymous"

  _db_make_post(owner, flask.request.form["text"], None, flask.request.form.get("image")) # TODO SOON

  return flask.redirect(flask.url_for('index'))

@wib.route('/post/<int:post_id>')
def show_post(post_id):
  assert typeof(post_id, int)
  return [get_post(post_id), get_sub_posts(post_id)]

@wib.route('/reboot', methods=['GET', 'POST'])
def reboot():
  """
  Used for exiting the wsgi interface, allowing code to resume
  """
  if flask.request.method == 'POST':
    if hash.md5(flask.request.form['REBOOTCODE']) == "3DA5DAC093EFA65422CBB22AF4588C65":
      exit()
  return '<form method="post"><p><input type=text name=REBOOTCODE><p><input type=submit value=REBOOT></form>'
