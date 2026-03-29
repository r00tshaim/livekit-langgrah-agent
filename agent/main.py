import asyncio
from dotenv import load_dotenv

from livekit.agents import AgentSession, Agent, JobContext
from livekit.plugins import langchain
from livekit.plugins import deepgram  # ✅ NEW
from livekit.plugins import silero

from agent.graph import build_graph

load_dotenv()


class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful voice assistant.",
        )


async def entrypoint(ctx: JobContext):
    graph = build_graph()

    session = AgentSession(
        # LLM (unchanged)
        llm=langchain.LLMAdapter(graph=graph),

        # 🔥 Deepgram speech pipeline
        #stt=deepgram.STT(),     # speech → text
        #tts=deepgram.TTS(),     # text → speech
        stt=deepgram.STT(model="nova-2"),  # better accuracy
        tts=deepgram.TTS(),  # nicer voice
        vad=silero.VAD.load(), # voice detection
    )

    await session.start(
        room=ctx.room,
        agent=VoiceAgent(),
    )


from livekit.agents import WorkerOptions
from livekit.agents.cli import run_app

if __name__ == "__main__":
    run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )