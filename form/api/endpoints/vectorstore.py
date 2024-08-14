from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from loguru import logger

from form.db.db_operations import DatabaseOperations, get_db_ops
from form.models.exceptions import DatabaseOperationError
from form.models.requests import Document
from form.models.responses import (
    EmbeddingDataOutput,
    EmbeddingWithDistanceOutput,
)
from form.vectorstore.pgvector import OpenAIEmbeddings

router = APIRouter()


@router.put(
    "/upsert_embedding",
    status_code=204,
    response_class=Response,
    description="Upsert an embedding in the database",
)
async def upsert_embedding(
    doc: Document,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> Response:
    try:
        await db_ops.upsert_embedding(doc)
        return Response(status_code=204)
    except DatabaseOperationError as e:
        logger.error(f"Database error while upserting embedding: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/upsert_embeddings",
    status_code=204,
    response_class=Response,
    description="Upsert multiple embeddings in the database",
)
async def upsert_embeddings(
    embeddings: List[Document],
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> Response:
    try:
        await db_ops.upsert_embeddings(embeddings)
        return Response(status_code=204)
    except DatabaseOperationError as e:
        logger.error(f"Database error while upserting embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_all_embeddings",
    response_model=List[EmbeddingDataOutput],
    description="Get all available embeddings from the database",
)
async def get_all_embeddings(
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[EmbeddingDataOutput]:
    try:
        embeddings = await db_ops.get_all_embeddings()
        return [
            EmbeddingDataOutput(
                embedding_id=embedding.embedding_id,
                content=embedding.content,
                embedding=embedding.embedding.tolist(),
                properties=embedding.properties,
                created_at=embedding.created_at,
                last_updated_at=embedding.last_updated_at,
            )
            for embedding in embeddings
        ]
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching all embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_embedding/{embedding_id}",
    response_model=EmbeddingDataOutput,
    description="Get embedding data from the database",
)
async def get_embedding(
    embedding_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> EmbeddingDataOutput:
    try:
        embedding = await db_ops.get_embedding(embedding_id)
        return EmbeddingDataOutput(
            embedding_id=embedding.embedding_id,
            content=embedding.content,
            embedding=embedding.embedding.tolist(),
            properties=embedding.properties,
            created_at=embedding.created_at,
            last_updated_at=embedding.last_updated_at,
        )
    except ValueError as _:
        raise HTTPException(
            status_code=404, detail=f"Embedding {embedding_id} does not exist"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching embedding {embedding_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_embeddings/",
    response_model=List[EmbeddingDataOutput],
    description="Get multiple embeddings from the database",
)
async def get_embeddings(
    embedding_id: Annotated[List[UUID], Query()],
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[EmbeddingDataOutput]:
    try:
        embeddings = await db_ops.get_embeddings(embedding_id)
        return [
            EmbeddingDataOutput(
                embedding_id=embedding.embedding_id,
                content=embedding.content,
                embedding=embedding.embedding.tolist(),
                properties=embedding.properties,
                created_at=embedding.created_at,
                last_updated_at=embedding.last_updated_at,
            )
            for embedding in embeddings
        ]
    except ValueError as _:
        raise HTTPException(status_code=404, detail="None of the embeddings exist")
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/delete_embedding/{embedding_id}",
    status_code=204,
    description="Delete an embedding from the database",
)
async def delete_embedding(
    embedding_id: UUID,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> Response:
    try:
        await db_ops.delete_embedding(embedding_id)
        return Response(status_code=204)
    except ValueError as _:
        raise HTTPException(
            status_code=404, detail=f"Embedding {embedding_id} does not exist"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database error while deleting embedding {embedding_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/delete_embeddings",
    status_code=204,
    description="Delete multiple embeddings from the database",
)
async def delete_embeddings(
    embedding_id: Annotated[List[UUID] | None, Query()] = None,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> Response:
    try:
        await db_ops.delete_embeddings(embedding_id)
        return Response(status_code=204)
    except ValueError as _:
        raise HTTPException(status_code=404, detail="None of the embeddings exist")
    except DatabaseOperationError as e:
        logger.error(f"Database error while deleting embeddings {embedding_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_embedding_by_content",
    response_model=EmbeddingDataOutput,
    description="Get embedding data from the database by content",
)
async def get_embedding_by_content(
    content: str,
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> EmbeddingDataOutput:
    try:
        embedding = await db_ops.get_embedding_by_content(content)
        if not embedding:
            raise HTTPException(
                status_code=404,
                detail=f"Embedding with content {content} does not exist",
            )
        return EmbeddingDataOutput(
            embedding_id=embedding.embedding_id,
            content=embedding.content,
            embedding=embedding.embedding.tolist(),
            properties=embedding.properties,
            created_at=embedding.created_at,
            last_updated_at=embedding.last_updated_at,
        )
    except DatabaseOperationError as e:
        logger.error(
            f"Database error while fetching embedding with content {content}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_nearest_embeddings",
    response_model=List[EmbeddingWithDistanceOutput],
    description="Get nearest embeddings from the database",
)
async def get_nearest_embeddings(
    query: str,
    limit: int = 5,
    distance_type: str = "l2_distance",
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[EmbeddingWithDistanceOutput]:
    try:
        async with OpenAIEmbeddings() as openai_embedding:
            target_embedding = await openai_embedding.get_embedding(query)
        embeddings = await db_ops.get_nearest_embeddings(
            target_embedding, limit, distance_type
        )
        return [
            EmbeddingWithDistanceOutput(
                embedding_id=embedding.embedding_id,
                content=embedding.content,
                embedding=embedding.embedding.tolist(),
                properties=embedding.properties,
                created_at=embedding.created_at,
                last_updated_at=embedding.last_updated_at,
                distance=distance,
            )
            for embedding, distance in embeddings
        ]
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching nearest embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_embeddings_within_distance",
    response_model=List[EmbeddingDataOutput],
    description="Get embeddings within a certain distance from the database",
)
async def get_embeddings_within_distance(
    query: str,
    distance: float,
    distance_type: str = "l2_distance",
    db_ops: DatabaseOperations = Depends(get_db_ops),
) -> List[EmbeddingDataOutput]:
    try:
        async with OpenAIEmbeddings() as openai_embedding:
            target_embedding = await openai_embedding.get_embedding(query)
        embeddings = await db_ops.get_embeddings_within_distance(
            target_embedding, distance, distance_type
        )
        return [
            EmbeddingDataOutput(
                embedding_id=embedding.embedding_id,
                content=embedding.content,
                embedding=embedding.embedding.tolist(),
                properties=embedding.properties,
                created_at=embedding.created_at,
                last_updated_at=embedding.last_updated_at,
            )
            for embedding in embeddings
        ]
    except DatabaseOperationError as e:
        logger.error(f"Database error while fetching embeddings within distance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/embed_query/{query}",
    response_model=List[float],
    description="Get embedding for a query",
)
async def embed_query(
    query: str,
) -> List[float]:
    try:
        async with OpenAIEmbeddings() as openai_embedding:
            embedding = await openai_embedding.get_embedding(query)
        return embedding
    except ValueError as _:
        raise HTTPException(status_code=404, detail="Embedding does not exist")
    except Exception as e:
        logger.error(f"Error while embedding query {query}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/embed_queries",
    response_model=List[List[float]],
    description="Get embeddings for multiple queries",
)
async def embed_queries(
    queries: Annotated[List[str] | None, Query()] = None,
) -> List[List[float]]:
    try:
        async with OpenAIEmbeddings() as openai_embedding:
            embeddings = await openai_embedding.get_embeddings(queries)
        return [embedding for embedding in embeddings]
    except ValueError as _:
        raise HTTPException(status_code=404, detail="Embedding does not exist")
    except Exception as e:
        logger.error(f"Error while embedding queries {queries}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
