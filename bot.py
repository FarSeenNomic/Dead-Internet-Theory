import requests
import time
import random
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

URL = "http://localhost:5000/create"

COOKIES = {
    "session": os.getenv("SESSION_COOKIE")
}

def generate_post():
    banned = ["quantum", "protocol", "error", "sector", "detected"]

    for _ in range(3):
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": """
Write a short, realistic social media post like a college student.

Rules:
- 1–2 sentences max
- casual tone
- slightly imperfect grammar is fine
- no weird or random nonsense
- no sci-fi, bots, or "quantum" stuff
- avoid hashtags unless natural

Examples:
- "lowkey didn’t understand anything in lecture today"
- "why is campus food actually decent today"
- "i need coffee asap"
"""
                }
            ]
        )

        post = res.choices[0].message.content.strip()

        if not any(word in post.lower() for word in banned):
            return post

    return "lowkey tired today"
def create_post(content):
    data = {
        "text": content,
        "anon": "",
        "image": ""
    }

    res = requests.post(URL, data=data, cookies=COOKIES)
    print(res.status_code, content)


def main():
    real_posts = [
    "lowkey tired as hell today",
    "this class makes no sense",
    "anyone else not do the reading",
    "gym was mid today",
    "need food asap",
    "bro i need a nap asap",
    "why is campus wifi so bad",
    "lowkey should start studying but not feeling it",
    "i swear time moves faster on weekdays",
    "im so behind on everything rn",
    ]

    used_posts = set()

    for i in range(random.randint(10, 20)):
        while True:
            if random.random() < 0.4:
                post = random.choice(real_posts)
            else:
                try:
                    post = generate_post()
                except:
                    post = random.choice(real_posts)

            if post not in used_posts:
                used_posts.add(post)
                break

        if random.random() < 0.3:
            post = post.lower()
        
        if random.random() < 0.3:
            post = post.replace(".", "")

        create_post(post)
        time.sleep(random.randint(3, 10))


if __name__ == "__main__":
    main()