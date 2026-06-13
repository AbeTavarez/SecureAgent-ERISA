from state import AgentState
from langchain_groq import ChatGroq
from langchain.messages import SystemMessage
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv
load_dotenv()
langfuse_handler = CallbackHandler()

model = ChatGroq(model="qwen/qwen3-32b", temperature=0)

PROMPT = """You're a helpful assistance"""


def llm_call(state: AgentState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model.invoke(
                [SystemMessage(content=PROMPT)] + state["messages"],
                config={"callbacks": [langfuse_handler]},
            )
        ],
    }
