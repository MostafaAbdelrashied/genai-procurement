from typing import List, Optional

from openai import AsyncOpenAI
from procurement.utils.config import get_settings


class OpenAIEmbeddings:
    def __init__(
        self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"
    ):
        self.api_key = api_key or get_settings().open_ai_config.openai_api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

    @staticmethod
    def _process_text(text: str) -> str:
        return text.strip().lower().replace("\n", " ")

    async def get_embedding(self, content: str) -> List[float]:
        formatted_text = self._process_text(content)
        embedding_object = await self.client.embeddings.create(
            input=[formatted_text], model=self.model
        )
        return embedding_object.data[0].embedding

    async def get_embeddings(self, contents: List[str]) -> List[List[float]]:
        formatted_texts = [self._process_text(text) for text in contents]
        embedding_object = await self.client.embeddings.create(
            input=formatted_texts, model=self.model
        )
        return [data.embedding for data in embedding_object.data]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
