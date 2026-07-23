import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("NVIDIA_API_KEY")

r = requests.get(
    "https://integrate.api.nvidia.com/v1/models",
    headers={
        "Authorization": f"Bearer {key}"
    }
)

print(r.status_code)
print(r.text[:1000])