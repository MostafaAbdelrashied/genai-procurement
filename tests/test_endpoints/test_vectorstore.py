from __future__ import annotations

from uuid import uuid4

import pytest

from tests.test_endpoints.fixtures.vectorstore_fixture import (
    assert_valid_embedding,
)


@pytest.mark.parametrize(
    "endpoint, payload",
    [
        ("/vectorstore/upsert_embedding", "sample_document"),
        ("/vectorstore/upsert_embeddings", "sample_documents"),
    ],
)
def test_upsert(client, endpoint, payload, request):
    response = client.put(endpoint, json=request.getfixturevalue(payload))
    assert response.status_code == 204


def test_get_all_embeddings(client):
    response = client.get("/vectorstore/get_all_embeddings")
    assert response.status_code == 200
    embeddings = response.json()
    assert isinstance(embeddings, list)
    assert len(embeddings) >= 3


@pytest.mark.parametrize(
    "embedding_id, expected_status",
    [
        ("sample_document_uuid", 200),
        (uuid4(), 404),
    ],
)
def test_get_embedding(client, embedding_id, expected_status, request):
    if isinstance(embedding_id, str):
        embedding_id = request.getfixturevalue(embedding_id)
    response = client.get(f"/vectorstore/get_embedding/{embedding_id}")
    assert response.status_code == expected_status
    if expected_status == 200:
        embedding_data = response.json()
        assert_valid_embedding(embedding_data)
    else:
        assert response.json() == {"detail": f"Embedding {embedding_id} does not exist"}


@pytest.mark.parametrize(
    "num_ids, expected_status",
    [
        (2, 200),
        (1, 200),
        (0, 404),
    ],
)
def test_get_embeddings(client, sample_documents_uuids, num_ids, expected_status):
    ids = sample_documents_uuids[:num_ids] + [uuid4()] * (2 - num_ids)
    response = client.get(
        f"/vectorstore/get_embeddings/?embedding_id={ids[0]}&embedding_id={ids[1]}"
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        embeddings = response.json()
        assert isinstance(embeddings, list)
        assert len(embeddings) == num_ids
        for embedding in embeddings:
            assert_valid_embedding(embedding)
    else:
        assert response.json() == {"detail": "None of the embeddings exist"}


def test_get_embedding_by_content(client, sample_document):
    response = client.get(
        f"/vectorstore/get_embedding_by_content?content={sample_document['content']}"
    )
    assert response.status_code == 200
    embedding_data = response.json()
    assert_valid_embedding(embedding_data)
    assert embedding_data["content"] == sample_document["content"]


@pytest.mark.parametrize(
    "limit, distance_type",
    [
        (3, "l2_distance"),
        (5, "cosine_distance"),
    ],
)
def test_get_nearest_embeddings(client, limit, distance_type):
    response = client.get(
        f"/vectorstore/get_nearest_embeddings?query=test&limit={limit}&distance_type={distance_type}"
    )
    assert response.status_code == 200
    nearest_embeddings = response.json()
    assert isinstance(nearest_embeddings, list)
    assert len(nearest_embeddings) <= limit
    for embedding in nearest_embeddings:
        assert "embedding_id" in embedding
        assert "content" in embedding
        assert "distance" in embedding


def test_get_embeddings_within_distance(client):
    response = client.get(
        "/vectorstore/get_embeddings_within_distance?query=test&distance=1.0&distance_type=l2_distance"
    )
    assert response.status_code == 200
    embeddings = response.json()
    assert isinstance(embeddings, list)
    for embedding in embeddings:
        assert "embedding_id" in embedding
        assert "content" in embedding


@pytest.mark.parametrize(
    "query, num_queries",
    [
        ("test%20query", 1),
        ("test%20query1&queries=test%20query2", 2),
    ],
)
def test_embed_queries(client, query, num_queries):
    response = client.get(f"/vectorstore/embed_queries?queries={query}")
    assert response.status_code == 200
    embeddings = response.json()
    assert isinstance(embeddings, list)
    assert len(embeddings) == num_queries
    for embedding in embeddings:
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)


@pytest.mark.parametrize(
    "embedding_id, expected_status",
    [
        ("sample_document_uuid", 204),
        (uuid4(), 404),
    ],
)
def test_delete_embedding(client, embedding_id, expected_status, request):
    if isinstance(embedding_id, str):
        embedding_id = request.getfixturevalue(embedding_id)
    response = client.delete(f"/vectorstore/delete_embedding/{embedding_id}")
    assert response.status_code == expected_status
    if expected_status == 404:
        assert response.json() == {"detail": f"Embedding {embedding_id} does not exist"}


@pytest.mark.parametrize(
    "num_ids, expected_status",
    [
        (0, 404),
        (1, 204),
        (2, 204),
    ],
)
def test_delete_embeddings(client, sample_documents_uuids, num_ids, expected_status):
    ids = sample_documents_uuids[:num_ids] + [uuid4()] * (2 - num_ids)
    response = client.delete(
        f"/vectorstore/delete_embeddings?embedding_id={ids[0]}&embedding_id={ids[1]}"
    )
    assert response.status_code == expected_status
    if expected_status == 404:
        assert response.json() == {"detail": "None of the embeddings exist"}
