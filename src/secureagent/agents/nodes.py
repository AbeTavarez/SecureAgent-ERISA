from langchain_groq import ChatGroq
from langchain.messages import SystemMessage
from langfuse.langchain import CallbackHandler
from langgraph.graph import END
from langchain.messages import AIMessage, ToolMessage
from secureagent.agents.state import AgentState, TriageDecision

# Tools
from secureagent.prompts.agent_triage_classifier import TRIAGE_PROMPT
from secureagent.tools.crm_tools import get_health_status, get_client_by_tax_id, add_note_to_profile
from secureagent.prompts.agent_tool_calling import AGENT_TOOL_CALLING_PROMPT

from dotenv import load_dotenv

load_dotenv()

langfuse_handler = CallbackHandler()

# Model Tools
tools = [get_health_status, get_client_by_tax_id, add_note_to_profile]
tools_by_name = {tool.name: tool for tool in tools}

# Model
model = ChatGroq(model="qwen/qwen3-32b", temperature=0)
model_with_tools = model.bind_tools(tools)


def llm_call(state: AgentState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content=AGENT_TOOL_CALLING_PROMPT)] + state["messages"],
                config={"callbacks": [langfuse_handler]},
            )
        ],
    }


def tool_node(state: AgentState):
    
    result = []
    last_message = state["messages"][-1]
    
    # Only AIMessages have tool_calls
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: AgentState):
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    last_message = state["messages"][-1]

    # If the LLM makes a tool call, then perform an action
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


def triage_node(state: AgentState):
    """Classify the next action"""
    triage_model = model.with_structured_output(TriageDecision)

    decision = triage_model.invoke(
        [SystemMessage(content=TRIAGE_PROMPT)] + state["messages"],
        config={"callbacks": [langfuse_handler]},
    )

    return {
        "current_triage": decision,
        "metadata": {
            **state.get("metadata", {}),
            "last_triage": decision.model_dump_json(),
        }
    }