import json

from procurement.agents.base_agent import BaseAgent


class NoteTakingAgent(BaseAgent):
    async def process(self, input_prompt: str, form: dict, messages: list):
        sys_prompt = self._get_sys_prompt(form, messages)
        response = await self._call_openai(
            model_name="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": input_prompt},
            ],
        )
        return response

    def _get_sys_prompt(self, form: dict, messages: list):
        return (
            messages
            + "\n\n"
            + self._read_prompt(
                "server/prompts/note_taking_sys_prompt.txt",
                form=json.dumps(form, indent=2),
            )
        )
