from langchain_core.messages import SystemMessage
from pydantic import SecretStr
from langchain_groq import ChatGroq


from app.config import settings
from app.ai_engineering.agent.prompts.prompts import SYSTEM_PROMPT
from app.schemas.agent import AgentState
from app.ai_engineering.agent.tools.OpenaiTools import tools


async def call_model(state: AgentState):
    api_key = settings.GROQ_API_KEY
    if isinstance(api_key, SecretStr):
        api_key = api_key.get_secret_value()
    if not api_key or not api_key.strip():
        raise ValueError("GROQ_API_KEY is not configured.")

    llm = ChatGroq(
        model=settings.GROQ_MODEL_NAME,
        api_key=api_key,
        temperature=0.7,
        timeout=30.0,
        max_retries=2,
    ).bind_tools(tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}
