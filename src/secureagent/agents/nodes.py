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
from secureagent.prompts.agent_final_reply import FINAL_REPLY_PROMPT
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


def route_after_triage(state: AgentState):
    """Route the agent based upon the triage decision"""

    triage = state["current_triage"]

    # If the triage is None, escalate to a human
    if triage is None:
        return "human_escalation"

    # If the confidence is low, escalate to a human
    if triage.confidence < 0.6:
        return "human_escalation"

    routing = {
        "CRM_LOOKUP": "crm_lookup",
        "CRM_UPDATE": "crm_update",
        "RAG_SEARCH": "rag_search",
        "HUMAN_INTERVENTION": "human_escalation",
        "FINAL_REPLY": "final_reply",
    }

    return routing.get(triage.next_action, "human_escalation")


def crm_lookup_node(state: AgentState):
    """Lookup the client in the CRM"""
    triage = state["current_triage"]
    tax_id = triage.tax_id if triage else None

    if not tax_id:
        return {
            "messages": [AIMessage(content="I need a tax ID to look up the client.")]
        }
    
    try:
        result = get_client_by_tax_id({"tax_id": tax_id})
    except Exception as e:
        result = str(e)
    
    return {
        "messages": [AIMessage(content=f"CRM lookup result: {result}")]
    }


def crm_update_node(state: AgentState):
    """Update the client in the CRM"""
    
    triage = state["current_triage"]
    tax_id = triage.tax_id if triage else None
    client_id = triage.client_id if triage else None
    note_content = triage.note_content if triage else None
    author = triage.author if triage else None

    if not tax_id or not client_id or not note_content or not author:
        return {
            "messages": [AIMessage(content="I need a tax ID, note content, and author to update the client.")]
        }
    
    try:
        result = add_note_to_profile(client_id, note_content, tax_id, author)
    except Exception as e:
        result = str(e)
    
    return {
        "messages": [AIMessage(content=f"CRM update result: {result}")]
    }


def rag_search_node(state: AgentState):
    """Search the RAG database"""
    triage = state["current_triage"]
    query = (triage.search_query if triage else None) or "regulatory query"

    # TODO: Implement RAG search
    result = {
        "source": "RAG Stub",
        "content": "This is a stub for the RAG search."
    }
    
    return {
        "retrieved_context": [result],
        "messages": [AIMessage(content=f"[RAG Stub would search regulations for {query}]")]
    }


def human_escalation_node(state: AgentState):
    """Escalate to a human"""
    triage = state["current_triage"]
    reason = triage.reasoning if triage else None

    return {
        "messages": [AIMessage(content=f"I'm escalating this to a human specialist with the following reason: {reason}")]
    }


def final_reply_node(state: AgentState):
    """Generate a final reply"""
    reply = model.invoke(
        [SystemMessage(content=FINAL_REPLY_PROMPT)] + state["messages"],
        config={"callbacks": [langfuse_handler]},
    )

    return {"messages": [reply]}