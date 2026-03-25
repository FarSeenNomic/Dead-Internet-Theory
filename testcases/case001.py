import requests
# compiles and runs

# API Create account

s = requests.Session()

form_data = {
    "username": "example_user2",
    "password": "password"
}

print("register")
response = s.post("http://localhost:5000/register", data=form_data)
assert response.status_code == 200

print("login")
response = s.post("http://localhost:5000/login", data=form_data)
assert response.status_code == 200

print("create")
response = s.post("http://localhost:5000/create", data={"text": "butts"})
assert response.status_code == 200

# API Login and get API key

# API Make post

# API get post
