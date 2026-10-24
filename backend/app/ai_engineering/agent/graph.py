from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from app.schemas.agent import AgentState
from app.ai_engineering.agent.nodes.llm import call_model
from app.ai_engineering.agent.tools.OpenaiTools import tools


def build_graph(checkpointer):
    builder = StateGraph(AgentState)
    builder.add_node("llm", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", tools_condition)
    builder.add_edge("tools", "llm")
    return builder.compile(checkpointer=checkpointer)
