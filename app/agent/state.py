"""
Agent state definition for LangGraph.
"""

from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The state of the agent throughout the conversation.
    
    Attributes:
        messages: The conversation history with message accumulation
        user_phone: The user's WhatsApp phone number (thread_id)
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_phone: str
