import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- 1. PYDANTIC SCHEMAS (Data Contracts) ---
class ErisaPolicy(BaseModel):
    policy_id: str 
    plan_type: str # 401K, 403b, 'Defines Benefits' 
    compliance_status: str  # 'Compliant', 'PendingAudit'
    last_review: str 
    
class ClientMetadata(BaseModel):
    client_id: str
    company_name: str 
    tax_id: str 
    account_status: str # 'Active', 'Suspended' 
    erisa_policies: List[ErisaPolicy]
    compliance_notes: List[str] = []
    
class ClientNoteRequest(BaseModel):
    client_id: str = Field(..., description="Target client unique identifier")
    note_content: str = Field(..., description="The triage/compliance note to append")
    author: str = Field(default="SecureAgent-ERISA")

class NoteResponse(BaseModel):
    status: str 
    timestamp: datetime
    note_id: str