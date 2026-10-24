from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.ai_engineering.agent.prompts.prompts import SYSTEM_PROMPT
from app.schemas.agent import AgentState
from app.ai_engineering.agent.tools.OpenaiTools import tools
from app.services.codecraft.connection import BASE_URL


async def call_model(state: AgentState):
    if not settings.OPENAI_API_KEY or not settings.OPENAI_API_KEY.strip():
        raise ValueError("OPENAI_API_KEY is not configured.")
    llm = ChatOpenAI(
        model=settings.MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
        base_url=BASE_URL,
        temperature=0.7,
        timeout=30.0,
        max_retries=2,
    ).bind_tools(tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}
