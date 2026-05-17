import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a sarcastic physics teacher who loves to make fun of students questions.",
    messages=[
        {
            "role": "user",
            "content": "Explain what an LLM is in 2 sentences."
        }
    ]
)

print(response.content[0].text)