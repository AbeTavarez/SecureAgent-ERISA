from state import AgentState
from langchain_groq import ChatGroq
from langchain.messages import SystemMessage
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import ToolNode, tools_condition

# Tools
from tools.crm_api import get_health_status

from dotenv import load_dotenv

load_dotenv()

langfuse_handler = CallbackHandler()

# Model Tools
tools = [get_health_status]
tool_node = ToolNode(tools)

model = ChatGroq(model="qwen/qwen3-32b", temperature=0)
model_with_tools = model.bind_tools(tools)


PROMPT = """You're a helpful assistance"""


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
