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
  print(response.status_code)

try:
  response = user1.post("http://localhost:5000/login", data=user1_data)
  assert response.status_code == 200
  print(f"login {user1_data['username']}")
except AssertionError:
  print(response.status_code)

try:
  response = user1.post("http://localhost:5000/create", data={"text": "War isn't Hell. War is war, and Hell is Hell. And of the two, war is a lot worse. There are no innocent bystanders in Hell."})
  assert response.status_code == 200
  print(f"create {user1_data['username']}")
except AssertionError:
  print(response.status_code)

#Text username in use
#Test password minimum length
#Test password maximum length

user2.post("http://localhost:5000/register", data=user2_data)
user2.post("http://localhost:5000/login", data=user2_data)
print(f"register and login {user2_data['username']}")

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
  print(response.status_code)

user3.post("http://localhost:5000/register", data=user3_data)
user3.post("http://localhost:5000/login", data=user3_data)
print(f"register and login {user3_data['username']}")


try:
  response = user2.get(f"http://localhost:5000/user.json/@{user1_data['username']}").json()
  print(f"Made {user2_data['username']} view all posts from {user1_data['username']}")
  print(response)
except Exception as e:
  print(e)

post2like = response[0]["snowflake"]
post2follow = response[0]["owner_snowflake"]

try:
  response = user2.post(f"http://localhost:5000/like.json/{post2like}")
  print(f"Made {user2_data['username']} like {user1_data['username']}")
  print(response.content)
  print(response.json())
except Exception as e:
  print(e)

try:
  response = user2.post(f"http://localhost:5000/follow.json/{post2follow}")
  print(f"Made {user2_data['username']} follow {user1_data['username']}")
  print(response.content)
  print(response.json())
except Exception as e:
  print(e)

try:
  response = user2.post(f"http://localhost:5000/reply/{post2like}", data={"text": "To the ends of the earth, friend."})
  print(f"Reply {user2_data['username']}")
  assert response.status_code == 200
except AssertionError as e:
  print(e)

try:
  response = user3.post(f"http://localhost:5000/reply/{post2like}", data={"text": "Baah."})
  print(f"Reply {user3_data['username']}")
  assert response.status_code == 200
except AssertionError as e:
  print(e)


#try:
#  print("Rebooting!")
#  response = user3.post(f"http://localhost:5000/reboot", data={"REBOOTCODE": "butts"})
#except requests.exceptions.ConnectionError as e:
#  print(e)
