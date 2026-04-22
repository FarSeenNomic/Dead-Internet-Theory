import requests
import praw
import json

reddit = praw.Reddit(client_id='Ub_MbSQVQLJpNA',
                     client_secret='mF3B12mx8xTyZlBF9-_kERX_IeA',
                     user_agent='Windows:python3.school_DIT:v1 (by /u/Imanton1)',check_for_async=False)

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

posts = 0
for submission in reddit.subreddit('foodporn').hot():
  if submission.url and submission.url[~0] != "/":
    text = submission.title
    if "]" in text[:10]:
      text = text.split("] ", 2)[1]
    if submission.selftext:
      text = f"{text}. {submission.selftext}"

    if len(text) > 140:
      continue

    print({"text": text, "image_url": submission.url})

    user1.post("http://localhost:5000/create", data={"text": text, "image_url": submission.url})
    posts += 1
    if posts >= 3:
      break
