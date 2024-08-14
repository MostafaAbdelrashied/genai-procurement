from form.agents.base_agent import BaseAgent


class ConversationAgent(BaseAgent):
    async def process(
        self,
        input_prompt: str,
        first_empty_field: list,
        rule_validation: str,
        specialist_response: str,
    ):
        sys_prompt = self._get_sys_prompt(first_empty_field, rule_validation)
        response = await self._call_openai(
            model_name="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": input_prompt},
                {"role": "assistant", "content": specialist_response},
            ],
        )
        return response

    def _get_sys_prompt(self, first_empty_field: list, rule_validation: str) -> str:
        return self._read_prompt(
            "form/prompts/conversation_sys_prompt.txt",
            first_empty_field=first_empty_field[-1],
            rule_validation=rule_validation,
        )
