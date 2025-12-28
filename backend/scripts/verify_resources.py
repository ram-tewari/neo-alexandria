import httpx
import asyncio

API_URL = "http://localhost:8000/resources"

async def list_resources():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                print(f"Total resources: {data.get('total', 0)}")
                for item in data.get('items', []):
                    print(f"- {item.get('title')} ({item.get('url')})")
            else:
                print(f"Failed to list resources: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(list_resources())
