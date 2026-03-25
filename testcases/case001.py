import requests
# compiles and runs

# API Create account

requests.Session()

form_data = {
    "username": "example_user",
    "password": "password"
}

s.post("http://localhost/register", data=form_data)
assert response.status_code == 200

s.post("http://localhost/login", data=form_data)
assert response.status_code == 200

s.post("http://localhost/create", data={"text": "butts"})
assert response.status_code == 200

# API Login and get API key

# API Make post

# API get post
