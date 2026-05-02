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
person("Tech", """
You are a tech enthusiast named TechWiz. You write for Twitter.
You love gadgets, new apps, and emerging technologies.
You often share opinions on trending tech, reviews, and cool discoveries.
Keep posts casual, curious, and slightly playful.
""", {"username": "TechWiz", "password": "Tech4ever!"}, "https://i.pinimg.com/474x/69/b1/7d/69b17d689ab0025c0331d50e58b8d861.jpg?nii=t"),

person("Robotics", """
You are a robotics enthusiast named RoboticWiz. You write for Twitter.
You love robots, new robot inventions, and emerging ai robot technologies.
You often share opinions on trending tech, reviews, and cool discoveries about robotics.
Keep posts casual, curious, and slightly playful.
""", {"username": "RoboticWiz", "password": "Robotics4ever!"}, "https://cdn.pixabay.com/photo/2019/11/08/10/34/cyber-4610993_1280.jpg"),


]

Tech_genius = personas[0]
print(Tech_genius.new)
Tech_genius.login()
print(Tech_genius.new)
if Tech_genius.new:
  output = Tech_genius.persona_generate("Please write a tweet about the following: You really enjoy making hardware for personal computers. There is a picture of a motherboard attached.")
  Tech_genius.create_post(output, 'https://tse1.mm.bing.net/th/id/OIP.73jSGVW0Xdd9Fk3OM_dERAHaFj?rs=1&pid=ImgDetMain&o=7&rm=3')
  print("post 1 done.")

  output = Tech_genius.persona_generate("Please write a tweet about the following: You really enjoy blasting your offer letter to Google. There is a picture of an offer letter from Google giving a position of Developer as the job title attached.")
  Tech_genius.create_post(output, 'https://imgv2-1-f.scribdassets.com/img/document/660112992/original/a3345b5699/1710773585?v=1')
  print("post 2 done.")

  output = Tech_genius.persona_vision("Please write a tweet about the following.", 'https://images.pexels.com/photos/1779487/pexels-photo-1779487.jpeg?auto=compress&cs=tinysrgb&w=1200')
  Tech_genius.create_post(output, 'https://images.pexels.com/photos/1779487/pexels-photo-1779487.jpeg?auto=compress&cs=tinysrgb&w=1200')
  print("post 3 done.")


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
message.txt
