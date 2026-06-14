from fastapi import APIRouter, status, HTTPException
from datetime import datetime
import uuid
from langchain.tools import tool

from schemas.api_models import (
    ClientMetadata,
    ErisaPolicy,
    NoteResponse,
    ClientNoteRequest,
)

router = APIRouter()

# Hardcoded in-memory state representing the enterprise database backend
MOCK_CLIENTS_DB = {
    "95-1234567": ClientMetadata(
        client_id="cli_99011",
        company_name="Contoso Retirement Solutions",
        tax_id="95-1234567",
        account_status="Active",
        erisa_policies=[
            ErisaPolicy(
                policy_id="pol_401k_abc",
                plan_type="401k",
                compliance_status="Compliant",
                last_review="2026-01-15",
            )
        ],
        compliance_notes=["Initial onboarding compliance review completed."],
    )
}


@tool
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

    # Lookup client in mock db
    print(tax_id)
    client_profile = MOCK_CLIENTS_DB.get(tax_id)

    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with Tax ID '{tax_id}' not found in CRM database.",
        )
    return client_profile


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

    # Get client by the id
    target_client = None
    for profile in MOCK_CLIENTS_DB.values():
        if profile.client_id == payload.client_id:
            target_client = profile
            break

    if not target_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{payload.client_id}' does not exist.",
        )

    # Append the structured note content to the profile
    timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    formatted_note = f"[{timestamp_str} | {payload.author}]: {payload.note_content}"
    target_client.compliance_notes.append(formatted_note)

    # Return a clean confirmation contract back to the agent loop
    return NoteResponse(
        status="Success", timestamp=datetime.utcnow(), note_id=str(uuid.uuid4())
    )
