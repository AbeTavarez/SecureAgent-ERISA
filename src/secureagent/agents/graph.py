from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
import uuid

from secureagent.agents.state import AgentState
from secureagent.agents.nodes import llm_call, tool_node, should_continue

from IPython.display import Image, display

from dotenv import load_dotenv

load_dotenv()

# Memory
memory = InMemorySaver()

# Build agent workflow
agent_workflow = StateGraph(AgentState)


# ===== Nodes =====
agent_workflow.add_node("llm_call", llm_call)
agent_workflow.add_node("tool_node", tool_node)



# ==== Edges =====
agent_workflow.add_edge(START, "llm_call")
agent_workflow.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_workflow.add_edge("tool_node", "llm_call")


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