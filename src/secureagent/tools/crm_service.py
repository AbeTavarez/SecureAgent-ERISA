from secureagent.schemas.api_models import (
    ClientMetadata,
    ErisaPolicy,
    NoteResponse,
)
from datetime import datetime

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


def append_note_to_client(client_id: str, note_content: str, author: str = "SecureAgent-ERISA") -> NoteResponse:
    """Append a note to a client's compliance history."""
    db_client = MOCK_CLIENTS_DB.get(client_id)
    if db_client is None:
        raise ClientNotFoundError(client_id)
    
    db_client.compliance_notes.append(note_content)
    return NoteResponse(
        client_id=client_id,
        note_content=note_content,
        author=author,
        timestamp=datetime.now().isoformat(),
    )   
