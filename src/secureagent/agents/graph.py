from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from typing import cast

from secureagent.agents.state import AgentState
from secureagent.agents.nodes import llm_call, tool_node, should_continue

from IPython.display import Image, display

from dotenv import load_dotenv

load_dotenv()


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
agent = agent_workflow.compile()


# Visualize Graph
def get_graph_diagram():
    try:
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception:
        print("Additional dependencies required.")

#! Remove after creating CLI
if __name__ == "__main__":

    user_prompt = input("Enter prompt: ")

    messages = [HumanMessage(content=user_prompt)]

    initial_state = cast(
        AgentState,
        {
            "messages": messages,
            "retrieved_context": [],
            "current_triage": None,
            "metadata": {},
        },
    )

    messages = agent.invoke(initial_state)

    for message in messages["messages"]:
        print(message)
