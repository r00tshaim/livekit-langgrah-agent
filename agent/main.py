import asyncio
import json
import os
from dotenv import load_dotenv

from livekit.agents import AgentSession, Agent, JobContext
from livekit.plugins import langchain
from livekit.plugins import deepgram
from livekit.plugins import silero

# SIP outbound calls via LiveKit API
from livekit import api

from agent.graph import build_graph
from agent.property_data import get_vectorstore

load_dotenv()


class RealEstateVoiceAgent(Agent):
    """
    Real estate marketing voice agent for newly launched housing schemes.
    Warm, conversational, and proactive in helping clients find their dream home.
    """
    def __init__(self):
        super().__init__(
            instructions=(
                "You're Alex, a friendly real estate consultant helping people find their dream home. "
                "Sound natural and conversational - like chatting with a friend over coffee. "
                "Be proactive, show enthusiasm, and gently guide toward scheduling property visits. "
                "Keep responses concise for voice conversation."
            ),
        )


async def entrypoint(ctx: JobContext):
    # Initialize property vector store on startup
    print("🏠 Loading property database...")
    try:
        get_vectorstore()
        print("✅ Property database loaded successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize property database: {e}")

    # Build the LangGraph agent
    graph = build_graph()

    # Create agent session
    session = AgentSession(
        llm=langchain.LLMAdapter(graph=graph),
        stt=deepgram.STT(model="nova-2"),
        tts=deepgram.TTS(),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=RealEstateVoiceAgent(),
    )

    # Handle outbound SIP calls if phone number provided in metadata
    metadata = ctx.job.metadata or ""
    try:
        dial_info = json.loads(metadata)
        phone_number = dial_info.get("phone_number")
    except (json.JSONDecodeError, TypeError):
        phone_number = metadata.strip() if metadata else None

    if phone_number:
        print(f"📞 Outbound call requested to {phone_number}")
        try:
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
                    sip_call_to=phone_number,
                    participant_identity=phone_number,
                    wait_until_answered=True,
                )
            )
            print(f"✅ Outbound call to {phone_number} connected!")
            await ctx.wait_for_participant(identity=phone_number)

        except api.TwirpError as e:
            print(f"❌ SIP call failed: {e.message}")
            print(f"   SIP status code: {e.metadata.get('sip_status_code')}")
            print(f"   SIP status: {e.metadata.get('sip_status')}")


from livekit.agents import WorkerOptions
from livekit.agents.cli import run_app

if __name__ == "__main__":
    run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="realestate-voice-agent",
        )
    )
