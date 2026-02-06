import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

models = response.json()['data']

print("\n✅ Available FREE/Cheap models for email generation:\n")

for model in models:
    # Filter for cheap models good for text generation
    if model['pricing']['prompt'] < 0.0005:  # Less than $0.50 per 1M tokens
        print(f"Model: {model['id']}")
        print(f"  Cost: ${float(model['pricing']['prompt'])*1000000:.3f} per 1M tokens")
        print(f"  Context: {model['context_length']} tokens")
        print()