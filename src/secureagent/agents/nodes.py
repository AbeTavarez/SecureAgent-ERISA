from langchain_groq import ChatGroq
from langchain.messages import SystemMessage
from langfuse.langchain import CallbackHandler
from langgraph.graph import END
from langchain.messages import AIMessage, ToolMessage
from secureagent.agents.state import AgentState

# Tools
from secureagent.tools.crm_tools import get_health_status, get_client_by_tax_id, add_note_to_profile

from dotenv import load_dotenv

load_dotenv()

langfuse_handler = CallbackHandler()

# Model Tools
tools = [get_health_status, get_client_by_tax_id, add_note_to_profile]
tools_by_name = {tool.name: tool for tool in tools}

# Model
model = ChatGroq(model="qwen/qwen3-32b", temperature=0)
model_with_tools = model.bind_tools(tools)


PROMPT = """You're an ERISA compliance agent that can look up client information and add notes to their profile.
You can use the following tools to get information about the client and add notes to their profile:
- get_health_status: Get the health status of the CRM API.
- get_client_by_tax_id: Look up a client CRM profile by Tax ID (e.g. '95-1234567').
- add_note_to_profile: Append a compliance note to a client's profile.
"""


def llm_call(state: AgentState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content=PROMPT)] + state["messages"],
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