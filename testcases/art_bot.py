import requests
import json

from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

openai_client = OpenAI() # you would need to set the OPENAI_API_KEY environment variable for this to work
#export OPENAI_API_KEY="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"
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

def generate_image(prompt):
    """
    Generate an image from text and return its URL.
    """
    try:
        result = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="500x500"
        )
        return result.data[0].url
    except Exception as e:
        print("Image generation error:", e)
        return None

gpt_parameter = {
    "max_tokens": 140,
    "stop": ['=','\n']
}

prompt = "You love art. Please write a abstract tweet about it."
form_data = {
    "username": "example_user3",
    "password": "passwords"
}

s = requests.Session()
output = GPT4_request(prompt, gpt_parameter).strip()
image_url = generate_image(output)


response = s.post("http://localhost:5000/login", data=form_data)

response = s.post("http://localhost:5000/create", data={"text": output, "image": image_url})

print(output)
