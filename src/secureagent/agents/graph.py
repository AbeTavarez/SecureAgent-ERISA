from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
import uuid

from secureagent.agents.state import AgentState
from secureagent.agents.nodes import (
    triage_node,
    route_after_triage,
    crm_lookup_node,
    crm_update_node,
    rag_search_node,
    human_escalation_node,
    final_reply_node,
)

from IPython.display import Image, display

from dotenv import load_dotenv

load_dotenv()

# Memory
memory = InMemorySaver()

# Build agent workflow
agent_workflow = StateGraph(AgentState)


# ===== Nodes =====
agent_workflow.add_node("triage", triage_node)
agent_workflow.add_node("crm_lookup", crm_lookup_node)
agent_workflow.add_node("crm_update", crm_update_node)
agent_workflow.add_node("rag_search", rag_search_node)
agent_workflow.add_node("human_escalation", human_escalation_node)
agent_workflow.add_node("final_reply", final_reply_node)


# ==== Edges =====
agent_workflow.add_edge(START, "triage")  # Start with triage/classifier
agent_workflow.add_conditional_edges(
    "triage",
    route_after_triage,
    {
    "crm_lookup": "crm_lookup",
    "crm_update": "crm_update",
    "rag_search": "rag_search",
    "human_escalation": "human_escalation",
    "final_reply": "final_reply",
},
)

agent_workflow.add_edge("crm_lookup", "final_reply")
agent_workflow.add_edge("crm_update", "final_reply")
agent_workflow.add_edge("rag_search", "final_reply")
agent_workflow.add_edge("human_escalation", END)
agent_workflow.add_edge("final_reply", END)

# Compile the graph
agent = agent_workflow.compile(checkpointer=memory)


# Visualize Graph
def get_graph_diagram():
    try:
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception:
        print("Additional dependencies required.")


def run_agent(prompt: str, thread_id: str | None = None) -> AgentState:
    """Run the ERISA agent with the given prompt and memory."""

    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

    return agent.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
