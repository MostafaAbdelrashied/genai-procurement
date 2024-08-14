import json
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from form.utils.config import get_settings


class BaseAgent(ABC):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=get_settings().open_ai_config.api_key)

    @abstractmethod
    async def process(self, input_prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def _get_sys_prompt(self) -> str:
        pass

    @staticmethod
    def _read_prompt(file_path: str, **kwargs) -> str:
        with open(file_path, "r") as file:
            content = file.read()
            return content.format(**kwargs)

    async def _call_openai(
        self,
        model_name: str,
        messages: list,
        max_tokens: int = 4096,
        response_format={"type": "json_object"},
        **kwargs,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            response_format=response_format,
            **kwargs,
        )
        return json.loads(response.choices[0].message.content)
