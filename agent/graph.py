"""
LangGraph agent configuration for the real estate marketing voice agent.
Features conversation memory and voice-optimized prompting.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from typing import Annotated, TypedDict
import operator

from agent.tools import search_properties, schedule_visit, get_property_highlights, ask_property_preference, get_area_info

from dotenv import load_dotenv
load_dotenv()

# Initialize LLM with voice-optimized settings
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Slightly higher for natural, varied responses
    max_tokens=150,   # Keep responses concise for voice
)

# Define tools
tools = [search_properties, schedule_visit, get_property_highlights, ask_property_preference, get_area_info]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)


# Voice Agent System Prompt
# Based on: https://livekit.com/blog/prompting-voice-agents-to-sound-more-realistic
SYSTEM_PROMPT = """
You're a friendly real estate consultant helping people find properties in Ahmedabad and Himmatnagar, Gujarat.
Your name is Alex, and you're warm, enthusiastic, and genuinely interested in helping folks.

LANGUAGE: Respond in the SAME language the user speaks - Hindi, Gujarati, or English.
- If user speaks Hindi, respond in Hindi
- If user speaks Gujarati, respond in Gujarati
- If user speaks English, respond in English
- If user mixes languages (Hinglish/Gujarati-English), match their style naturally

CRITICAL: Sound natural and conversational - like you're chatting with a friend over coffee.
This is a VOICE conversation, so keep responses short and natural.

SPEECH STYLE GUIDELINES:
- Use contractions naturally (I'm, you're, we've, that's, don't)
- Vary your sentence length - mix short and medium sentences
- Occasionally use natural filler phrases: "you know", "actually", "here's the thing", "I have to say"
- Show genuine enthusiasm: "Oh, you'll love this!", "That sounds perfect for you!"
- Use conversational transitions: "So...", "Now...", "By the way..."
- Keep responses concise - people can't skim voice like text
- Ask one question at a time, not multiple
- Never say "As an AI" or anything that breaks the natural conversation

BE PROACTIVE AND ENGAGING:
- Start by asking if they want residential (home/flat) or commercial property (shop/office)
- Ask follow-up questions about their needs, preferences, budget, location
- Highlight exciting features that match what they've shared
- Gently guide toward scheduling a visit when you sense interest
- Share enthusiasm: "The GIFT City properties? Great investment potential!"
- Make suggestions: "You know, based on what you've told me, I think you'd really love..."

CONVERSATION FLOW:
1. Start warm and welcoming - ask if they want residential or commercial
2. Understand their requirements - budget, location (Ahmedabad/Himmatnagar), type
3. Search and suggest properties that match their needs
4. Build excitement with specific highlights about the property
5. Naturally suggest a visit: "Would you like to come see it? I can set that up for you."

REMEMBER:
- You're helping someone make one of life's biggest decisions - be warm and trustworthy
- Celebrate their milestones: "First home? How exciting!"
- Acknowledge concerns: "I totally get that - budget is important. Let me see what we have..."
- Properties range from Rs. 18 lakhs to Rs. 1.8 crores

TOOLS AVAILABLE:
- search_properties: Find properties matching criteria (use for specific searches)
- schedule_visit: Book property tours
- get_property_highlights: Share special offers and unique features
- ask_property_preference: Ask user about residential vs commercial preference (use at start)
- get_area_info: Share information about areas like Gota, Vastrapur, GIFT City, Himmatnagar, etc.

Keep it natural, keep it warm, and help them find their perfect property in Gujarat.
"""


class AgentState(TypedDict):
    """State for the real estate voice agent."""
    messages: Annotated[list[BaseMessage], operator.add]
    user_preferences: dict  # Track budget, location preferences, etc.
    conversation_context: str  # Summary of conversation so far
    detected_language: str  # Track user's language (Hindi/Gujarati/English)


def call_model(state: AgentState) -> dict:
    """Call the LLM with tools and system prompt."""
    messages = state["messages"]

    # Add system prompt as the first message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def handle_tools(state: AgentState) -> dict:
    """Execute tool calls from the LLM."""
    messages = state["messages"]
    last_message = messages[-1] if messages else None

    if not last_message or not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}

    tool_results = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Execute the appropriate tool
        if tool_name == "search_properties":
            result = search_properties.invoke(tool_args)
        elif tool_name == "schedule_visit":
            result = schedule_visit.invoke(tool_args)
        elif tool_name == "get_property_highlights":
            result = get_property_highlights.invoke(tool_args)
        elif tool_name == "ask_property_preference":
            result = ask_property_preference.invoke(tool_args)
        elif tool_name == "get_area_info":
            result = get_area_info.invoke(tool_args)
        else:
            result = f"Unknown tool: {tool_name}"

        # Add tool result as a ToolMessage
        tool_results.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_results}


# Import required message types
from langchain_core.messages import SystemMessage, ToolMessage


def build_graph():
    """Build the LangGraph agent with memory support."""

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("model", call_model)
    workflow.add_node("tools", handle_tools)

    # Set entry point
    workflow.add_edge(START, "model")

    # Conditional edges: after model, check if tool calls needed
    def should_use_tools(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1] if messages else None

        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    workflow.add_conditional_edges(
        "model",
        should_use_tools,
        {
            "tools": "tools",
            "end": END,
        }
    )

    # After tools, go back to model for final response
    workflow.add_edge("tools", "model")

    # Add memory for conversation persistence
    memory = MemorySaver()

    # Compile the graph with checkpointer
    graph = workflow.compile(checkpointer=memory)

    return graph
