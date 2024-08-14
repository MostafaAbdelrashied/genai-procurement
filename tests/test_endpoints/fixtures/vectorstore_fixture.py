import pytest

from form.utils.text_handler import convert_str_to_uuid


@pytest.fixture
def sample_document():
    return {
        "content": "This is a test document",
        "properties": {"key": "value"},
    }


@pytest.fixture
def sample_documents():
    return [
        {
            "content": f"This is test document {i}",
            "properties": {"key": "value"},
        }
        for i in range(1, 3)
    ]


@pytest.fixture
def sample_document_uuid(sample_document):
    return convert_str_to_uuid(sample_document["content"])


@pytest.fixture
def sample_documents_uuids(sample_documents):
    return [convert_str_to_uuid(doc["content"]) for doc in sample_documents]


def assert_valid_embedding(embedding_data):
    assert isinstance(embedding_data, dict)
    assert "embedding_id" in embedding_data
    assert "content" in embedding_data
    assert "embedding" in embedding_data
    assert "properties" in embedding_data
    assert "created_at" in embedding_data
    assert "last_updated_at" in embedding_data
