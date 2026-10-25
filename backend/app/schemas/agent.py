from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Conversation messages, accumulated across turns."""
    summary:str = None
