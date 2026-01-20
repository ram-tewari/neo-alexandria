"""Check chunks for existing resource via API."""
import requests

TOKEN = open("test_token.txt").read().strip()
RESOURCE_ID = "e638a6d6-6134-4d40-9127-c2c503695b3a"

headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.get(
    f"http://127.0.0.1:8000/resources/{RESOURCE_ID}/chunks",
    headers=headers
)

if response.status_code == 200:
    chunks = response.json()
    print(f"✅ Chunks found: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i}: {len(chunk['content'])} chars")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
