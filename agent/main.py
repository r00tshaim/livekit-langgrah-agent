import asyncio
import json
import os
from dotenv import load_dotenv

from livekit.agents import AgentSession, Agent, JobContext
from livekit.plugins import langchain
from livekit.plugins import deepgram
from livekit.plugins import silero
from livekit.plugins import sarvam

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
                "Namaste! You're Priya, a warm and friendly real estate consultant helping families find their perfect home. "
                "Speak in a natural, conversational tone - like chatting with a friend or family member. "
                "Be respectful, patient, and genuinely interested in understanding their needs. "
                "Show appropriate enthusiasm while remaining grounded and trustworthy. "
                "Gently guide conversations toward scheduling property site visits. "
                "Keep responses clear and concise for voice conversation."
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
        stt=sarvam.STT(
                language="unknown",  # Auto-detect language, or use "en-IN", "hi-IN", etc.
                model="saaras:v3",
                mode="transcribe"
        ),
        tts=sarvam.TTS(
                target_language_code="en-IN",
                model="bulbul:v3",
                speaker="priya"  # Female: priya, simran, ishita, kavya | Male: aditya, anand, rohan
        ),
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
            ctx.shutdown()          # Shutdown agent if SIP call fails, since it's a critical part of the use case
    else:
        print("ℹ️ No phone number provided for outbound call. Agent will only interact with in-room participants.")


from livekit.agents import WorkerOptions
from livekit.agents.cli import run_app

if __name__ == "__main__":
    run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="realestate-voice-agent",
        )
    )
