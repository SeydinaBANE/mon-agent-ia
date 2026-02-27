from langchain_groq import ChatGroq
from agent.state import AgentState
from dotenv import load_dotenv
load_dotenv()

llm =ChatGroq(model="openai/gpt-oss-120b")


def call_llm(state: AgentState) -> AgentState:
    """Nœud principal : appelle le LLM avec l'historique."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Routeur : décide si on continue ou on s'arrête."""
    last_message = state["messages"][-1]


    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"