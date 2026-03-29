from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agent.tools import get_weather

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

tools = [get_weather]

def build_graph():
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a helpful assistant. Use tools when needed."
    )

    return agent