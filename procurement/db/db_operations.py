from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Depends
from procurement.api.deps import get_session
from procurement.db.db_tables import Embedding, Message, Session
from procurement.models.exceptions import DatabaseOperationError
from procurement.models.requests import Document
from procurement.utils.text_handler import convert_str_to_uuid
from procurement.vectorstore.pgvector import OpenAIEmbeddings
from sqlalchemy import delete, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _execute_with_error_handling(self, operation):
        try:
            result = await operation()
            await self.db.commit()
            return result
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseOperationError(f"Database operation failed: {str(e)}")

    async def create_session(self, session_id: UUID, form_data: dict) -> UUID:
        async def operation():
            stmt = insert(Session).values(session_id=session_id, form_data=form_data)
            stmt = stmt.on_conflict_do_nothing(index_elements=["session_id"])
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def upsert_session(self, session_id: UUID, form_data: dict) -> None:
        async def operation():
            stmt = insert(Session).values(session_id=session_id, form_data=form_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["session_id"],
                set_=dict(last_updated_at=datetime.now(), form_data=form_data),
            )
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def upsert_message(
        self, message_id: UUID, session_id: UUID, prompt: str, response: str
    ) -> None:
        async def operation():
            stmt = insert(Message).values(
                message_id=message_id,
                session_id=session_id,
                prompt=prompt,
                response=response,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["message_id"],
                set_=dict(
                    message_id=message_id,
                    session_id=session_id,
                    prompt=prompt,
                    response=response,
                    created_at=datetime.now(),
                ),
            )
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def upsert_embedding(self, doc: Document) -> None:
        async def operation():
            embedding_id = convert_str_to_uuid(doc.content)
            async with OpenAIEmbeddings() as openai_embedding:
                embedding = await openai_embedding.get_embedding(doc.content)
            stmt = insert(Embedding).values(
                embedding_id=embedding_id,
                content=doc.content,
                embedding=embedding,
                properties=doc.properties,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["embedding_id"],
                set_=dict(
                    embedding_id=embedding_id,
                    content=doc.content,
                    embedding=embedding,
                    properties=doc.properties,
                    last_updated_at=datetime.now(),
                ),
            )
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def upsert_embeddings(self, docs: List[Document]) -> None:
        async def operation():
            values = []
            for doc in docs:
                async with OpenAIEmbeddings() as openai_embedding:
                    embedding = await openai_embedding.get_embedding(doc.content)
                values.append(
                    {
                        "embedding_id": convert_str_to_uuid(doc.content),
                        "content": doc.content,
                        "embedding": embedding,
                        "properties": doc.properties,
                        "last_updated_at": datetime.now(),
                    }
                )
            stmt = insert(Embedding).values(values)
            stmt = stmt.on_conflict_do_update(
                index_elements=["embedding_id"],
                set_=dict(
                    content=stmt.excluded.content,
                    embedding=stmt.excluded.embedding,
                    properties=stmt.excluded.properties,
                    last_updated_at=stmt.excluded.last_updated_at,
                ),
            )
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def get_embedding(self, embedding_id: UUID) -> Optional[Embedding]:
        async def operation():
            if not await self.check_embedding_exists(embedding_id):
                raise ValueError(f"Embedding {embedding_id} does not exist")
            query = select(Embedding).where(Embedding.embedding_id == embedding_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_error_handling(operation)

    async def get_embeddings(self, embedding_ids: List[UUID]) -> List[Embedding]:
        async def operation():
            if not await self.check_if_any_embedding_exists(embedding_ids):
                raise ValueError("None of the embeddings exist")
            query = select(Embedding).where(Embedding.embedding_id.in_(embedding_ids))
            result = await self.db.execute(query)
            return result.scalars().all()

        return await self._execute_with_error_handling(operation)

    async def delete_embedding(self, embedding_id: UUID) -> None:
        async def operation():
            if not await self.check_embedding_exists(embedding_id):
                raise ValueError(f"Embedding {embedding_id} does not exist")
            await self.db.execute(
                delete(Embedding).where(Embedding.embedding_id == embedding_id)
            )

        await self._execute_with_error_handling(operation)

    async def delete_embeddings(self, embedding_ids: List[UUID]) -> None:
        async def operation():
            if not await self.check_if_any_embedding_exists(embedding_ids):
                raise ValueError("None of the embeddings exist")
            await self.db.execute(
                delete(Embedding).where(Embedding.embedding_id.in_(embedding_ids))
            )

        await self._execute_with_error_handling(operation)

    async def get_embedding_by_content(self, content: str) -> Optional[Embedding]:
        async def operation():
            query = select(Embedding).where(Embedding.content == content)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_error_handling(operation)

    async def get_all_embeddings(self) -> List[Embedding]:
        async def operation():
            query = select(Embedding)
            result = await self.db.execute(query)
            return result.scalars().all()

        return await self._execute_with_error_handling(operation)

    async def get_nearest_embeddings(
        self,
        target_embedding: list,
        limit: int = 5,
        distance_type: Literal[
            "max_inner_product",
            "cosine_distance",
            "l1_distance",
            "l2_distance",
            "hamming_distance",
        ] = "l2_distance",
    ) -> List[Embedding]:
        async def operation():
            query = (
                select(
                    Embedding,
                    Embedding.embedding.__getattr__(distance_type)(
                        target_embedding
                    ).label("distance"),
                )
                .order_by(
                    Embedding.embedding.__getattr__(distance_type)(target_embedding)
                )
                .limit(limit)
            )

            result = await self.db.execute(query)
            return result.all()

        return await self._execute_with_error_handling(operation)

    async def get_embeddings_within_distance(
        self,
        target_embedding: list,
        distance: float,
        distance_type: Literal[
            "max_inner_product",
            "cosine_distance",
            "l1_distance",
            "l2_distance",
            "hamming_distance",
        ] = "l2_distance",
    ) -> List[Embedding]:
        async def operation():
            query = select(Embedding).filter(
                Embedding.embedding.__getattr__(distance_type)(target_embedding)
                < distance
            )
            result = await self.db.execute(query)
            return result.scalars().all()

        return await self._execute_with_error_handling(operation)

    async def get_session_data(self, session_id: UUID) -> Optional[Session]:
        async def operation():
            query = select(Session).where(Session.session_id == session_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_error_handling(operation)

    async def get_messages_for_session(
        self, session_id: UUID, create_if_not_exists: bool = False
    ) -> List[Message]:
        async def operation():
            if (
                not await self.check_session_exists(session_id)
                and not create_if_not_exists
            ):
                raise ValueError(f"Session {session_id} does not exist")
            query = (
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at)
            )
            result = await self.db.execute(query)
            return result.scalars().all()

        return await self._execute_with_error_handling(operation)

    async def delete_session(self, session_id: UUID) -> None:
        async def operation():
            if not await self.check_session_exists(session_id):
                raise ValueError(f"Session {session_id} does not exist")
            await self.db.execute(
                delete(Message).where(Message.session_id == session_id)
            )
            await self.db.execute(
                delete(Session).where(Session.session_id == session_id)
            )

        await self._execute_with_error_handling(operation)

    async def update_session_data(self, session_id: UUID, form_data: str) -> None:
        async def operation():
            if not await self.check_session_exists(session_id):
                raise ValueError(f"Session {session_id} does not exist")
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(form_data=form_data, last_updated_at=datetime.now())
            )
            await self.db.execute(stmt)

        await self._execute_with_error_handling(operation)

    async def get_all_sessions(self) -> List[Session]:
        async def operation():
            query = select(Session)
            result = await self.db.execute(query)
            return result.scalars().all()

        return await self._execute_with_error_handling(operation)

    async def check_session_exists(self, session_id: UUID) -> bool:
        async def operation():
            query = select(Session).where(Session.session_id == session_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None

        return await self._execute_with_error_handling(operation)

    async def check_embedding_exists(self, embedding_id: UUID) -> bool:
        async def operation():
            query = select(Embedding).where(Embedding.embedding_id == embedding_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None

        return await self._execute_with_error_handling(operation)

    async def check_if_any_embedding_exists(self, embedding_ids: List[UUID]) -> bool:
        async def operation():
            query = select(Embedding).where(Embedding.embedding_id.in_(embedding_ids))
            result = await self.db.execute(query)
            return result.scalars().all() != []

        return await self._execute_with_error_handling(operation)


async def get_db_ops(
    db_session: AsyncSession = Depends(get_session),
) -> DatabaseOperations:
    return DatabaseOperations(db_session)
