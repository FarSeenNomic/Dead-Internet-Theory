import requests
# compiles and runs

# API Create account

def test_register_endpoint():
    url = "http://localhost/register"

    form_data = {
        "username": "example_user",
        "password": "ExamplePassword123!"
    }

    response = requests.post(url, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    return data

# API Login and get API key

# API Make post

# API get post
