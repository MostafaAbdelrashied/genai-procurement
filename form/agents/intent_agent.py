from form.agents.base_agent import BaseAgent


class IntentAgent(BaseAgent):
    async def process(self, input_prompt: str, messages: str):
        sys_prompt = self._get_sys_prompt(messages)
        response = await self._call_openai(
            model_name="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": input_prompt},
            ],
        )
        return response

    def _get_sys_prompt(self, messages: str):
        return (
            messages + "\n\n" + self._read_prompt("form/prompts/intent_sys_prompt.txt")
        )
