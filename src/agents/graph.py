from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from state import AgentState
from typing import cast
from nodes import llm_call

from dotenv import load_dotenv
load_dotenv()

# Build agent workflow
agent_workflow = StateGraph(AgentState)

# Nodes
agent_workflow.add_node("llm_call", llm_call)


# Edges
agent_workflow.add_edge(START, "llm_call")

agent = agent_workflow.compile()


if __name__ == "__main__":
    
    user_prompt = input("Enter prompt: ")
    
    messages = [HumanMessage(content=user_prompt)]

    initial_state = cast(AgentState, {
        "messages": messages,
        "retrieved_context": [],
        "current_triage": None,
        "metadata": {},
    })

    messages = agent.invoke(initial_state)

    for message in messages["messages"]:
        print(message)