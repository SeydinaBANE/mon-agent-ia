from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from agent.state import AgentState
from agent.nodes import call_llm, should_continue
from dotenv import load_dotenv
load_dotenv()


@tool
def recherche_meteo(ville: str) -> str:
    """Retourne la météo d'une ville."""
    return f"Il fait 22°C et ensoleillé à {ville}."

@tool
def calculatrice(expression: str) -> str:
    """Évalue une expression mathématique simple."""
    try:
        return str(eval(expression))
    except:
        return "Erreur de calcul"

tools = [recherche_meteo, calculatrice]
tool_node = ToolNode(tools)


from langchain_groq import ChatGroq
llm_with_tools = ChatGroq(model="openai/gpt-oss-120b").bind_tools(tools)

def call_llm_with_tools(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    graph = StateGraph(AgentState)


    graph.add_node("llm", call_llm_with_tools)
    graph.add_node("tools", tool_node)


    graph.set_entry_point("llm")


    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    #
    graph.add_edge("tools", "llm")

    return graph.compile()


agent = build_graph()