import requests

user1 = requests.Session()
user1_data = {
  "username": "CptHawkeye",
  "password": "teddybear"
}

#One user doesn't start with an @, the other does. Both should work equally.
user2 = requests.Session()
user2_data = {
  "username": "@BJHunnicutt",
  "password": "Peg&Erin"
}

user3 = requests.Session()
user3_data = {
  "username": "MajorCharlesEmersonWinchesterIII",
  "password": "DOCTOR"
}

try:
  response = user1.post("http://localhost:5000/register", data=user1_data)
  assert response.status_code == 200
  print(f"registered {user1_data['username']}")
except AssertionError:
  print("Error", response.status_code)

try:
  response = user1.post("http://localhost:5000/login", data=user1_data)
  assert response.status_code == 200
  print(f"login {user1_data['username']}")
except AssertionError:
  print("Error", response.status_code)

try:
  response = user1.post("http://localhost:5000/settings/profile", data={
    "bio": "I wonder how a degenerated person like that could have reached a position of responsibility in the Army Medical Corps.",
    "pfp": "https://64.media.tumblr.com/avatar_5562e40dd3bb_128.pnj",
    "displayname": '"Hawkeye" Pierce',
    })
  assert response.status_code == 200
  print(f"updated PFP {user1_data['username']}")
except AssertionError:
  print("Error", response.status_code)

try:
  response = user1.post("http://localhost:5000/create", data={"text": "War isn't Hell. War is war, and Hell is Hell. And of the two, war is a lot worse. There are no innocent bystanders in Hell."})
  assert response.status_code == 200
  print(f"create {user1_data['username']}")
except AssertionError:
  print("Error", response.status_code)

#Text username in use
#Test password minimum length
#Test password maximum length

user2.post("http://localhost:5000/register", data=user2_data)
user2.post("http://localhost:5000/login", data=user2_data)
user2.post("http://localhost:5000/settings/profile", data={
  "bio": "I'm a temporarily misassigned civilian.",
  "pfp": "https://i.etsystatic.com/32846439/r/il/99ddc5/3468026512/il_300x300.3468026512_hmbc.jpg",
  "displayname": 'Captain B.J. Hunnicutt',
  })
print(f"register, login, and update {user2_data['username']}")

"""

try:
  response = user3.post("http://localhost:5000/register", data=user1_data)
  assert response.status_code == 409
  print("Trying pasword of length 01")
  response = user3.post("http://localhost:5000/register", data={"username": "Anything01", "password": "0"})
  assert response.status_code == 422
  print("Trying pasword of length 99")
  response = user3.post("http://localhost:5000/register", data={"username": "Anything99", "password": "0"*99})
  assert response.status_code == 422
  print("Trying pasword of length 65")
  response = user3.post("http://localhost:5000/register", data={"username": "Anything65", "password": "0"*65})
  assert response.status_code == 422
  print("Trying pasword of length 64")
  response = user3.post("http://localhost:5000/register", data={"username": "Anything64", "password": "0"*64})
  assert response.status_code == 200
  print(f"{user3_data['username']} tried to make a user under the name {user2_data['username']}")
except AssertionError:
  print("Error", response.status_code)
"""

user3.post("http://localhost:5000/register", data=user3_data)
user3.post("http://localhost:5000/login", data=user3_data)
print(f"register and login {user3_data['username']}")

try:
  response = user2.get(f"http://localhost:5000/user.json/@{user1_data['username']}").json()
  print(f"Made {user2_data['username']} view all posts from {user1_data['username']}")
except Exception as e:
  print("Error", e)

print(response)

post2like = response[0]["snowflake"]
post2follow = response[0]["owner"]

try:
  response = user2.post(f"http://localhost:5000/like.json/{post2like}")
  print(f"Made {user2_data['username']} like {user1_data['username']}")
except Exception as e:
  print("Error", e)

try:
  response = user2.post(f"http://localhost:5000/follow.json/{post2follow}")
  print(f"Made {user2_data['username']} follow {user1_data['username']}")
except Exception as e:
  print("Error", e)

try:
  response = user2.post(f"http://localhost:5000/reply/{post2like}", data={"text": "To the ends of the earth, friend."})
  print(f"Reply {user2_data['username']}")
  assert response.status_code == 200
except AssertionError as e:
  print("Error", e)

try:
  response = user3.post(f"http://localhost:5000/reply/{post2like}", data={"text": "Baah."})
  print(f"Reply {user3_data['username']}")
  assert response.status_code == 200
except AssertionError as e:
  print("Error", e)

response = user3.post("http://localhost:5000/create", data={"text": "This nincompoop won't stop leaving these pictures on the job board.", "image": "https://64.media.tumblr.com/108628e7ab397985d6d4ea9aab7a43d1/c497e05a44d10137-8c/s1280x1920/2922a934ba2e6492d1b829a1626db05a38f88d52.jpg"})
print(f"image {user1_data['username']}")

try:
  response = user3.get('http://localhost:5000/posts.json/')
  assert response.status_code == 200
  print(response.content)
  post = response.json()[~0]

  try:
    response = user3.get(f"http://localhost:5000/post.json/{post['snowflake']}")
    print(response.content)
    print(response.json())
    assert response.status_code == 200
  except Exception as e:
    print("Error", e)

  try:
    response = user3.get(f"http://localhost:5000/replies.json/{post['snowflake']}")
    print(response.content)
    print(response.json())
    assert response.status_code == 200
  except Exception as e:
    print("Error", e)

  try:
    response = user3.get(f"http://localhost:5000/user.json/@{post['owner_username']}")
    print(response.content)
    print(response.json())
    assert response.status_code == 200
  except Exception as e:
    print("Error", e)
except Exception as e:
  print("Error", e)


#try:
#  print("Rebooting!")
#  response = user3.post(f"http://localhost:5000/reboot", data={"REBOOTCODE": "butts"})
#except requests.exceptions.ConnectionError as e:
#  print("Error", e)
