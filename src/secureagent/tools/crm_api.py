from fastapi import APIRouter, status, HTTPException
from secureagent.tools.crm_service import lookup_client_by_tax_id, append_note_to_client, ClientNotFoundError
from secureagent.schemas.api_models import (
    ClientMetadata,
    NoteResponse,
    ClientNoteRequest,
)

router = APIRouter()


@router.get(
    "/health", status_code=status.HTTP_200_OK, summary="Fetch API health status"
)
async def get_health_status() -> dict:
    """Fetch the current health status of the API application.
    Use this whenever you need to verify if the backend system is up and running.
    """
    return {"status": "ok"}


@router.get(
    "/clients/{tax_id}",
    response_model=ClientMetadata,
    status_code=status.HTTP_200_OK,
    summary="Fetch client profile by Tax ID",
)
async def get_client_by_tax_id(tax_id: str):
    """
    Triage step endpoint. Allows the agent to verify client
    existence and fetch active retirement plans.
    """

    try:
        return lookup_client_by_tax_id(tax_id)
    except ClientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with Tax ID '{tax_id}' not found in CRM database.",
        )


@router.post(
    "/clients/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Append agent compliance notes",
)
async def add_note_to_profile(payload: ClientNoteRequest):
    """
    Action step endpoint. Commits the agent's finalized
    regulatory determination back to the audit trail.
    """

    try:
        return append_note_to_client(payload.client_id, payload.note_content, payload.author)
    except ClientNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{payload.client_id}' does not exist.",
        )