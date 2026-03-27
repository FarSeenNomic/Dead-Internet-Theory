import requests
import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def GPT4_request(prompt, gpt_parameter):
  completion = client.chat.completions.create(
    model="lmstudio-community/Phi-3.1-mini-4k-instruct-GGUF",
    messages=[
      {"role": "user", "content": prompt}
    ],
    stop=gpt_parameter["stop"],
    max_tokens=gpt_parameter["max_tokens"]
  )
  return completion.choices[0].message.content

def get_embedding(text, model="text-embedding-ada-002"):
  text = text.replace("\n", " ")
  return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

gpt_parameter = {"engine": "text-davinci-003", "max_tokens": 140,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0,
                 "stop": ['=','\n']}

prompt = "You really enjoy mexican food. Please write a tweet about it."
form_data = {
    "username": "example_user2",
    "password": "password"
}

s = requests.Session()
output = GPT4_request(prompt, gpt_parameter).strip()
response = s.post("http://localhost:5000/login", data=form_data)
response = s.post("http://localhost:5000/create", data={"text": output})
print(output)