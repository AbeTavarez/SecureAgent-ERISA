from secureagent.agents.nodes import route_after_triage
from secureagent.agents.state import AgentState, TriageDecision
from langchain_core.messages import HumanMessage

def test_route_none_triage_escalates():
    """Test that when the triage is None, the agent routes to human escalation"""
    state = AgentState(
        messages=[
            HumanMessage(content="I need to look up a client's information by tax ID 95-1234567."),
        ],
        retrieved_context=[],
        current_triage=None,
        metadata={},
    )
    result = route_after_triage(state)
    assert result == "human_escalation"


def test_route_low_confidence_escalates():
    """Test that when the confidence is low, the agent routes to human escalation"""
    state = AgentState(
        messages=[
            HumanMessage(content="I need to look up a client's information by tax ID 95-1234567."),
        ],
        retrieved_context=[],
        current_triage=TriageDecision(
            next_action="CRM_LOOKUP",
            confidence=0.5,
            reasoning="The confidence is low because the user's request is not clear."
        ),
        metadata={},
    )
    result = route_after_triage(state)
    assert result == "human_escalation"