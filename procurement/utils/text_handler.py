import hashlib
import uuid
from uuid import UUID


def convert_str_to_uuid(id_str: str) -> UUID:
    if not id_str:
        raise ValueError("String ID cannot be empty.")
    if isinstance(id_str, UUID):
        return id_str
    hex_string = hashlib.md5(id_str.encode("UTF-8")).hexdigest()
    session_uuid = uuid.UUID(hex=hex_string)
    return session_uuid
