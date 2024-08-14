# agents_manager.py
import asyncio
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from form.db.db_operations import DatabaseOperations
from form.models.exceptions import AgentProcessingError
from form.utils.form_handler import (
    find_first_empty_field,
    find_rule_validation,
    match_if_form_updated,
    read_json,
    update_all_empty_fields,
)

from .conversation_agent import ConversationAgent
from .intent_agent import IntentAgent
from .note_taking_agent import NoteTakingAgent
from .specialist_agent import SpecialistAgent


class AgentsManager:
    def __init__(self, db_session: AsyncSession, session_id: UUID):
        self.db_ops = DatabaseOperations(db_session)
        self.session_id = session_id
        self.chat_history: List[Dict[str, str]] = []
        self.schema: Dict[str, Any] = {}
        self.intent_agent = IntentAgent()
        self.note_taking_agent = NoteTakingAgent()
        self.conversation_agent = ConversationAgent()
        self.specialist_agent = SpecialistAgent()

    async def initialize(self):
        self.chat_history = await self._get_session_history()
        self.schema = await self._get_latest_form_status()
        self.form_validation = self._get_form_validation()

    async def process_input(self, input_prompt: str) -> Dict[str, Any]:
        try:
            await self.initialize()
            self.chat_history.append(
                {"role": "user", "content": input_prompt, "from": "user"}
            )
            full_history_text = self._convert_history_to_text()

            intention_response = await self.intent_agent.process(
                input_prompt, messages=full_history_text
            )
            logger.info(f"Intention Agent: {intention_response['intent']}")

            if intention_response["to"] == "user":
                self.chat_history.append(intention_response)
                return {**intention_response, "schema": self.schema}

            # Run note-taking and specialist agents in parallel
            note_taking_task = asyncio.create_task(
                self._process_note_taking(input_prompt, full_history_text)
            )
            specialist_task = asyncio.create_task(
                self._process_specialist(input_prompt, full_history_text)
            )

            self.schema, specialist_clarification = await asyncio.gather(
                note_taking_task, specialist_task
            )

            conversation_response = await self._process_conversation(
                input_prompt=input_prompt, specialist_response=specialist_clarification
            )

            # Merge specialist response into conversation response
            conversation_response["specialist_response"] = specialist_clarification

            return conversation_response

        except Exception as e:
            logger.exception(f"Error in process_input: {str(e)}")
            raise AgentProcessingError(f"Failed to process input: {str(e)}")

    async def _process_note_taking(
        self, input_prompt: str, full_history_text: str
    ) -> Dict[str, Any]:
        round_i = 0
        while True:
            round_i += 1
            if round_i > 5:
                logger.info("Note-Taking Agent: Maximum iterations reached.")
                break
            logger.debug(f"Note-Taking Agent: Iteration {round_i}")
            note_response = await self.note_taking_agent.process(
                input_prompt,
                form=self.schema,
                form_val=self.form_validation,
                messages=full_history_text,
            )
            if self.schema == note_response["schema"]:
                logger.info("Note-Taking Agent: No new fields filled.")
                break
            # Only update the schema if the note-taking agent has filled in a new field
            update_all_empty_fields(self.schema, note_response["schema"])
            # In case of an update, the form should be updated with the new values
            match_if_form_updated(self.schema, note_response["schema"])
            if self.schema == note_response["schema"]:
                logger.info("Note-Taking Agent: Form filled successfully.")
                break

        return self.schema

    async def _process_specialist(
        self, input_prompt: str, full_history_text: str
    ) -> Optional[str]:
        specialist_response = await self.specialist_agent.process(
            input_prompt, messages=full_history_text
        )
        if specialist_response["is_clarification_needed"]:
            logger.info("Specialist Agent: clarification needed")
            return specialist_response["content"]
        logger.info("Specialist Agent: clarification not needed")
        return "None"

    async def _process_conversation(
        self, input_prompt: str, specialist_response: str
    ) -> Dict[str, Any]:
        first_empty_field = find_first_empty_field(self.schema)
        rule_validation = find_rule_validation(self.form_validation, first_empty_field)

        if first_empty_field:
            conversation_response = await self.conversation_agent.process(
                input_prompt=input_prompt,
                first_empty_field=first_empty_field,
                rule_validation=rule_validation,
                specialist_response=specialist_response,
            )
            self.chat_history.append(conversation_response)
            logger.info("Conversation Agent: Move to next field.")
            return {**conversation_response, "schema": self.schema}
        else:
            logger.info("All fields are filled.")
            return {
                "type": "conversation",
                "content": "The form was successfully filled.",
                "schema": self.schema,
                "from": "Conversation-Agent",
                "role": "assistant",
                "to": "user",
            }

    async def _get_session_history(self) -> List[Dict[str, str]]:
        messages = await self.db_ops.get_messages_for_session(
            self.session_id, create_if_not_exists=True
        )
        return [
            {
                "role": "user" if msg.prompt else "assistant",
                "content": msg.prompt or msg.response,
            }
            for msg in messages
        ]

    @staticmethod
    def _get_form_validation() -> Dict[str, Any]:
        return read_json(path="form/schemas/form_val.json")

    async def _get_latest_form_status(self) -> Dict[str, Any]:
        session_data = await self.db_ops.get_session_data(self.session_id)
        return (
            json.loads(session_data.form_data)
            if session_data
            else read_json(path="form/schemas/form.json")
        )

    def _convert_history_to_text(self) -> str:
        return "continue from history conversations: ...\n" + "\n".join(
            f'{message["role"]}: {message["content"]}' for message in self.chat_history
        )
