from fastapi import APIRouter, HTTPException

from form.models.responses import UUIDOutput
from form.utils.text_handler import convert_str_to_uuid

router = APIRouter()


@router.get(
    "/convert-string/{string_id}",
    response_model=UUIDOutput,
    description="Convert a string ID to UUID",
)
async def convert_to_uuid(string_id: str) -> UUIDOutput:
    try:
        return UUIDOutput(uuid=convert_str_to_uuid(string_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
