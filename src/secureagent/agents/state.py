from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Optional, Dict, Any
from typing import Literal

class TriageDecision(BaseModel):
    """Explicit structured prediction for the next step in execution."""
    
    next_action: str = Literal["RAG_SEARCH", "CRM_UPDATE", "HUMAN_INTERVENTION", "FINAL_REPLY"]
    
    reasoning: str = Field(
        description="Internal thought process driving the routing decision."
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0."
    )

    tax_id: str | None = None

    client_id: str | None = None

    note_content: str | None = None
    
    
class AgentState(TypedDict):
    """The unified state object for the workflow."""
    
    messages: Annotated[List[AnyMessage], add_messages]
    
    retrieved_context: List[Dict[str, Any]]
    
    # Explicit enterprise state tracking
    current_triage: Optional[TriageDecision]
    
    # Metadata tracking for internal compliance and auditing
    metadata: Dict[str, Any]