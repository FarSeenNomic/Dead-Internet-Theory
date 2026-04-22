import requests
import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
SITE_URL = "http://localhost:5000"

def think_seperate(response):
  if "</think>" in response:
    think, answer = response.split("</think>", 1)
    return think.strip(), answer.strip()
  else:
    return response, ""

def LLM4_request(prompt, dev=""):
  for _ in range(3):
    completion = client.chat.completions.create(
      model="*",
      messages=[
        {"role": "developer", "content": "Do not use any Emoji."},
        {"role": "developer", "content": dev},
        {"role": "user", "content": prompt},
      ],
    )
    think, message = think_seperate(completion.choices[0].message.content)
    if message:
      return message
  raise Exception("Thinking Error")

def LLM4_vision(prompt, img_url, dev=""):
  for _ in range(3):
    response = client.responses.create(
    model="*",
    input=[
      {"role": "developer", "content": "Do not use any Emoji."},
      {"role": "developer", "content": dev},
      {"role": "user","content": [
        {"type": "input_text", "text": prompt},
        {"type": "input_image", "image_url": f"{img_url}"},
        ]
      }
    ]
    )
    think, message = think_seperate(completion.output[0].content[0].text)
    if message:
      return message
  raise Exception("Thinking Error")

class person():
  def __init__(self, name, background, userpass, pfp):
    self.name = name
    self.background = background
    self.userpass = userpass
    self.pfp = pfp
    self.session = None
    self.new = None
    #self.login()

  def login(self):
    # Returns True if new account was made
    if self.session:
      return False
    self.session = requests.Session()

    self.new = False
    login_response = self.session.post(f"{SITE_URL}/login", data=self.userpass).status_code
    if login_response == 200:
      return False
    self.new = True

    print(f"registering account {self.name}")
    register_response = self.session.post(f"{SITE_URL}/register", data=self.userpass).status_code
    self.session.post(f"{SITE_URL}/login", data=self.userpass)

    if register_response != 200:
      print("Error 2")
      raise
    print(f"setting settings {self.name}")
    self.session.post(f"{SITE_URL}/settings/profile", data={
      "bio": LLM4_request("Please output your twitter bio:", self.background),
      "pfp": self.pfp,
      "displayname": self.name,
    })
    return True

  def persona_generate(self, text):
    return LLM4_request(text, self.background)

  def persona_vision(self, text, url):
    return LLM4_vision(text, url, self.background)

  def create_post(self, text, image=""):
    self.login()
    return self.session.post(f"{SITE_URL}/create", data={"text":text, 'image':image})

  def reply_to_post(self, replyto, text, image=""):
    self.login()
    return self.session.post(f"{SITE_URL}/reply/{replyto}", data={"text":text, 'image':image})

personas = [
person("Waffle", """
You are a girl foodie named Waffle. You will be writing for twitter.
You love all the foods of the world, and exploring new cusines.
""", {"username": "waffle", "password": "WaffleLovesFood2025!"}, "https://b.thumbs.redditmedia.com/rN5RfuAQgtXeIxfzDzHwBkG9VZZH_zy0tkhu447QyxA.png"),

person("Princess Celestia", """
You are Princess Celestia. You will be writing for twitter.
""", {"username": "radiantspark", "password": "princesscelestialpassw0rd"}, "https://cdn-img.fimfiction.net/story/k70b-1432583264-215301-medium"),

person("CodeNinja", """
You are a Programming student. You will be writing for twitter.
You sometimes post C code.
""", {"username": "codeninja_cs", "password": "password123"}, "https://resources.finalsite.net/images/f_auto,q_auto,t_image_size_1/v1705089776/darek12ncus/h54cs8ita4w715ztj04t/WhiteandBlueMinimalist2023CollegeFairFlyer1.png"),

person("Spock", """
You are Spock. You will be writing for twitter.
Make sure to always stay logical
""", {"username": "spock", "password": "1234567890spock"}, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR39UIrEhL7Ivb870S35f9CrCCxPuUkMDHARg&s"),
]

waffle = personas[0]
print(waffle.new)
waffle.login()
print(waffle.new)
if waffle.new:
  output = waffle.persona_generate("Please write a tweet about the following: You really enjoy food. There is a picture of an Iranian Koobideh Kebab attached.")
  waffle.create_post(output, 'https://i.redd.it/wow3cxa3bkrg1.jpeg')
  print("post 1 done.")

  output = waffle.persona_generate("Please write a tweet about the following: You really enjoy food. There is a picture of an Deepfried cod fish with garlic mayo attached.")
  waffle.create_post(output, 'https://i.redd.it/456qectjulrg1.jpeg')
  print("post 2 done.")

  output = waffle.persona_vision("Please write a tweet about the following.", 'https://i.redd.it/msfhnj32j8qg1.jpeg')
  waffle.create_post(output, 'https://i.redd.it/msfhnj32j8qg1.jpeg')
  print("post 3 done.")

"""
for persona in personas:
  resp = persona.persona_generate(f"Please choose to compose a tweet or not. You do not have to send, others will if you don't. Only send if it is in character. If you don't want to send, say NO, otherwise say the message. Say nothing else.\n")
  if "NO" not in resp:
    persona.create_post(resp)
"""#"""

response = waffle.session.get(f"{SITE_URL}/posts.json/")
tweet = response.json()[0]
print(tweet)

disp_tweet = {
  'owner_displayname': tweet['owner_displayname'],
  'text': tweet['text'],
}
img = tweet["image"]
reply_to = tweet["snowflake"]

for persona in personas:
  """
  if img:
    resp = persona.persona_vision(f"The following is a public tweet. You don't have to reply, others will if you don't. If you think it's good to reply to it, say YES otherwise say NO. Say nothing else.\n{tweet}\n", img)
  else:
    resp = persona.persona_generate(f"The following is a public tweet. You don't have to reply, others will if you don't. If you think it's good to reply to it, say YES otherwise say NO. Say nothing else.\n{tweet}\n")
  print(f"{persona.name} said {resp} to tweet {tweet}")
  if "yes" in resp.lower():
    if img:
      body = persona.persona_vision(f"Given this tweet, what do you want your reply to be? Keep it short and don't break character. {tweet}", img)
    else:
      body = persona.persona_generate(f"Given this tweet, what do you want your reply to be? Keep it short and don't break character. {tweet}")
    print(f"{body=}")
    persona.reply_to_post(reply_to, body)
  """
  if img:
    resp = persona.persona_vision(f"The following is a public tweet. You don't have to reply, others will if you don't. Only reply if it is in character. If you don't want to reply, say NO, otherwise say the reply. Say nothing else.\n{disp_tweet}\n", img)
  else:
    resp = persona.persona_generate(f"The following is a public tweet. You don't have to reply, others will if you don't. Only reply if it is in character. If you don't want to reply, say NO, otherwise say the reply. Say nothing else.\n{disp_tweet}\n")
  print(resp)
  if "NO" not in resp:
    persona.reply_to_post(reply_to, body)