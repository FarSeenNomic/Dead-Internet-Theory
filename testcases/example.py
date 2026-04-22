import requests
import json

user1 = requests.Session()
user1_data = {
  "username": "Hungry",
  "password": "lunch!@#$%^&*()"
}
resp = user1.post("http://localhost:5000/register", data=user1_data)
user1.post("http://localhost:5000/login", data=user1_data)
if resp.status_code:
  user1.post("http://localhost:5000/settings/profile", data={
    "bio": "Crossposting so much great food!",
    "pfp": "https://solcleanse.com/cdn/shop/files/Organic-Whole-Food-Meal-Pack-Plant-Based-Autumn-26-2_256x.webp",
    "displayname": 'My Lunch',
  })

for i in range(3):
  print(f"Post #{i}")
  user1.post("http://localhost:5000/create", data={"text": f"Hello #{i}"})

user1.post("http://localhost:5000/create", data={"text": f"Hello with image!", "image_url": "https://static1.e621.net/data/c8/42/c84273f16b7a1e7ecfa1c6db7fcebe8b.jpg"})