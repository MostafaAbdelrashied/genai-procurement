# agents/specialist_agent.py
from procurement.agents.base_agent import BaseAgent


class SpecialistAgent(BaseAgent):
    async def process(self, input_prompt: str, messages: str):
        sys_prompt = self._get_sys_prompt()
        response = await self._call_openai(
            model_name="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": f"Context: {messages}\n\nUser Query: {input_prompt}",
                },
            ],
        )
        return response

    def _get_sys_prompt(self) -> str:
        return self._read_prompt("procurement/prompts/specialist_sys_prompt.txt")
