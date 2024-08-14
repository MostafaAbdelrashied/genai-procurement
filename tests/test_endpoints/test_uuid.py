from __future__ import annotations


def test_convert_to_uuid_success(client):
    response = client.get("/uuid/convert-string/1")
    assert response.status_code == 200
    uuid_output = response.json()
    assert isinstance(uuid_output, dict)
    assert "uuid" in uuid_output.keys()
    assert uuid_output["uuid"] == "c4ca4238-a0b9-2382-0dcc-509a6f75849b"
