from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

class TriageDecision(BaseModel):
    """Explicit structured prediction for the next step in execution."""
    
    next_action: str = Field(
        description="The determined target action. Options: 'RAG_SEARCH', 'CRM_UPDATE', 'HUMAN_INTERVENTION', 'FINAL_REPLY'"
    )
    
    reasoning: str = Field(
        description="Internal thought process driving the routing decision."
    )
    
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0."
    )
    
    
class AgentState(TypedDict):
    """The unified state object for the workflow."""
    
    messages: Annotated[List[AnyMessage], add_messages]
    
    retrieved_context: List[Dict[str, Any]]
    
    # Explicit enterprise state tracking
    current_triage: Optional[TriageDecision]
    
    # Metadata tracking for internal compliance and auditing
    metadata: Dict[str, Any]