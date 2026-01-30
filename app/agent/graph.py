"""
LangGraph agent definition for StockPulse.
"""

from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.tools import (
    fetch_price,
    fetch_multiple_prices,
    get_stock_info,
    update_portfolio,
    remove_from_portfolio,
    get_portfolio,
    calculate_portfolio_stats,
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
)
from app.config import get_settings

# System prompt for the agent
SYSTEM_PROMPT = """You are StockPulse, a friendly and helpful AI financial assistant that helps users manage their stock portfolios via WhatsApp.

Your capabilities include:
1. **Stock Price Lookup**: Fetch current prices and daily changes for any stock
2. **Portfolio Management**: 
   - Add stocks to user's portfolio (when they buy shares)
   - Remove stocks from portfolio
   - Show portfolio holdings and performance
3. **Watchlist Management**:
   - Add stocks to watchlist for monitoring
   - Remove stocks from watchlist
   - Show current watchlist with prices
4. **Portfolio Analysis**: Calculate total portfolio value, gains/losses, and performance metrics

When users want to add stocks to their portfolio, extract:
- The ticker symbol (e.g., AAPL, TSLA)
- Number of shares
- Purchase price per share

Always be concise in your responses since this is WhatsApp. Use emojis sparingly to make messages friendly.

Format numbers nicely:
- Prices: $XXX.XX
- Percentages: X.XX%
- Use 📈 for gains and 📉 for losses

Remember the user's phone number is provided as user_phone in the state - use this for all portfolio and watchlist operations.

Important: Always use the tools provided to fetch real-time data. Never make up stock prices or portfolio information."""


# Define all tools
TOOLS = [
    fetch_price,
    fetch_multiple_prices,
    get_stock_info,
    update_portfolio,
    remove_from_portfolio,
    get_portfolio,
    calculate_portfolio_stats,
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
]

# Global agent instance
_agent = None
_checkpointer = None


def create_agent_graph(checkpointer=None):
    """Create the LangGraph agent."""
    settings = get_settings()
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=settings.openai_api_key
    )
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(TOOLS)
    
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM makes a tool call, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # Otherwise, end the conversation turn
        return "__end__"
    
    def call_model(state: AgentState) -> dict:
        """Call the LLM with the current state."""
        messages = state["messages"]
        user_phone = state.get("user_phone", "unknown")
        
        # Add system message with user context
        system_message = SystemMessage(
            content=f"{SYSTEM_PROMPT}\n\nCurrent user's phone number: {user_phone}"
        )
        
        # Call the model
        response = llm_with_tools.invoke([system_message] + list(messages))
        
        return {"messages": [response]}
    
    # Create the tool node
    tool_node = ToolNode(TOOLS)
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END,
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph with checkpointer for memory
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


def get_checkpointer():
    """Get or create the memory checkpointer for conversation memory."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = MemorySaver()
    return _checkpointer


def create_agent():
    """Create and return the agent with memory."""
    global _agent
    checkpointer = get_checkpointer()
    _agent = create_agent_graph(checkpointer)
    return _agent


def get_agent():
    """Get the agent instance, creating if necessary."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


async def process_message(user_phone: str, message: str) -> str:
    """
    Process a user message and return the agent's response.
    
    Args:
        user_phone: The user's WhatsApp phone number (used as thread_id)
        message: The user's message text
    
    Returns:
        The agent's response text
    """
    agent = get_agent()
    
    # Create the initial state
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "user_phone": user_phone
    }
    
    # Use the phone number as thread_id for conversation persistence
    config = {"configurable": {"thread_id": user_phone}}
    
    # Run the agent
    result = agent.invoke(initial_state, config)
    
    # Extract the final response
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            return last_message.content
    
    return "I'm sorry, I couldn't process your request. Please try again."
