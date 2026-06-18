from secureagent.schemas.api_models import (
    ClientMetadata,
    ErisaPolicy,
    NoteResponse,
)
from datetime import datetime
import uuid

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

class ClientNotFoundError(Exception):
    """Exception raised when a client is not found in the database."""
    def __init__(self, identifier: str):
        self.identifier = identifier


def lookup_client_by_tax_id(tax_id: str) -> ClientMetadata:
    """Lookup a client by their tax ID."""
    client = MOCK_CLIENTS_DB.get(tax_id)

    if client is None:
        raise ClientNotFoundError(tax_id)
    return client


def append_note_to_client(client_id: str, note_content: str, tax_id: str, author: str = "SecureAgent-ERISA") -> NoteResponse:
    """Append a note to a client's compliance history."""
    db_client = MOCK_CLIENTS_DB.get(tax_id)
    if db_client is None or db_client.client_id != client_id:
        raise ClientNotFoundError(f"Client with ID '{client_id}' and Tax ID '{tax_id}' not found in CRM database.")
    
    formatted_note = f"[{datetime.now().isoformat()} | {author}]: {note_content}"
    db_client.compliance_notes.append(formatted_note)
    return NoteResponse(
        status="Success",
        note_id=str(uuid.uuid4()),
        note_content=formatted_note,
        author=author,
        timestamp=datetime.now().isoformat(),
    )
