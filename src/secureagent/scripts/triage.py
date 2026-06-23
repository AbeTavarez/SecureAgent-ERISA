from secureagent.agents.state import AgentState
from secureagent.agents.nodes import triage_node
from langchain_core.messages import HumanMessage

def main():
    """Main function to run the triage script."""
    state = AgentState(
        messages=[
            HumanMessage(content="I need to look up a client's information by tax ID 95-1234567."),
        ],
        retrieved_context=[],
        current_triage=None,
        metadata={},
    )
    result = triage_node(state)
    print(result)

if __name__ == "__main__":
    main()