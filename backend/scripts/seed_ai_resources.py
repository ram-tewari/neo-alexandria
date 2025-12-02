import httpx
import asyncio

API_URL = "http://localhost:8000/resources"

AI_PUBLICATIONS = [
    {
        "url": "https://arxiv.org/abs/1706.03762",
        "title": "Attention Is All You Need",
        "description": "The seminal paper introducing the Transformer architecture, which has become the foundation for most modern NLP models.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2005.14165",
        "title": "Language Models are Few-Shot Learners (GPT-3)",
        "description": "This paper introduces GPT-3, demonstrating that scaling up language models greatly improves task-agnostic, few-shot performance.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2302.13971",
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "description": "Introduces LLaMA, a collection of foundation language models ranging from 7B to 65B parameters.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2303.08774",
        "title": "GPT-4 Technical Report",
        "description": "Technical report for GPT-4, a large multimodal model capable of processing image and text inputs and producing text outputs.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "description": "Proposes LoRA, a method to freeze pre-trained model weights and inject trainable rank decomposition matrices, reducing the number of trainable parameters.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "description": "Explores how generating a chain of thought—a series of intermediate reasoning steps—significantly improves the ability of large language models to perform complex reasoning.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2203.02155",
        "title": "Training language models to follow instructions with human feedback (InstructGPT)",
        "description": "Shows that fine-tuning with human feedback aligns language models better with user intent, making them more truthful and less toxic.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2307.09288",
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "description": "Details Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2305.10403",
        "title": "QLoRA: Efficient Finetuning of Quantized LLMs",
        "description": "Introduces QLoRA, an efficient finetuning approach that reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU.",
        "type": "paper"
    },
    {
        "url": "https://arxiv.org/abs/2310.06825",
        "title": "Mistral 7B",
        "description": "Introduces Mistral 7B, a 7-billion-parameter language model engineered for superior performance and efficiency.",
        "type": "paper"
    }
]

async def seed_resources():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, fetch existing resources to avoid duplicates
        existing_urls = set()
        try:
            response = await client.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    # The API returns 'source' as 'url' in some contexts, or we check both
                    url = item.get('url') or item.get('source')
                    if url:
                        existing_urls.add(url)
            print(f"Found {len(existing_urls)} existing resources.")
        except Exception as e:
            print(f"Warning: Could not fetch existing resources: {e}")

        print(f"Seeding AI publications to {API_URL}...")
        
        for pub in AI_PUBLICATIONS:
            if pub["url"] in existing_urls:
                print(f"Skipping existing: {pub['title']}")
                continue

            try:
                # Prepare form data as expected by the backend
                data = {
                    "url": pub["url"],
                    "title": pub["title"],
                    "description": pub["description"],
                    "type": pub["type"]
                }
                
                # Using json= for JSON body, which is what the backend expects for ResourceIngestRequest
                response = await client.post(API_URL, json=data)
                
                if response.status_code in [200, 201, 202]:
                    print(f"Successfully added: {pub['title']}")
                else:
                    print(f"Failed to add {pub['title']}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error adding {pub['title']}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(seed_resources())
