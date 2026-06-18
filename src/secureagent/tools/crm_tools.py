from langgraph.tools import tool
from secureagent.services.crm_service import lookup_client_by_tax_id, ClientNotFoundError, append_note_to_client
from secureagent.schemas.api_models import ClientMetadata, NoteResponse

@tool
def get_health_status() -> str:
    """
    Get the health status of the CRM API.
    Returns:
        A string indicating the health status of the CRM API.
    """
    return "The CRM API is healthy."

@tool
def get_client_by_tax_id(tax_id: str) -> ClientMetadata:
    """
    Look up a client CRM profile by Tax ID (e.g. '95-1234567').
    Returns company name, account status, ERISA policies, and compliance notes.
    
    Args:
        tax_id: The Tax ID of the client to look up.
    Returns:
        A ClientMetadata object containing the client's profile.
    """
    try:
        client = lookup_client_by_tax_id(tax_id)
        return client.model_dump_json()
    except ClientNotFoundError as e:
        raise ValueError(f"Client with Tax ID '{tax_id}' not found in CRM database.")


@tool
def add_note_to_profile(client_id: str, note_content: str, tax_id: str, author: str = "SecureAgent-ERISA") -> NoteResponse:
    """Append a compliance note to a client's profile.
    Args:
        client_id: The ID of the client to add the note to.
        note_content: The content of the note to add.
        tax_id: The Tax ID of the client to add the note to.
        author: The author of the note.
    Returns:
        A NoteResponse object containing the status of the note addition.
    """
    try:
        result = append_note_to_client(client_id, note_content, tax_id, author)
        return result.model_dump_json()
    except ClientNotFoundError as e:
        raise ValueError(f"Client with ID '{client_id}' and Tax ID '{tax_id}' not found in CRM database.")