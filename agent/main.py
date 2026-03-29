import asyncio
import json
import os
from dotenv import load_dotenv

from livekit.agents import AgentSession, Agent, JobContext
from livekit.plugins import langchain
from livekit.plugins import deepgram
from livekit.plugins import silero

# ✅ NEW: Official import for SIP outbound calls
from livekit import api

from agent.graph import build_graph

load_dotenv()


class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful voice assistant.",
        )


async def entrypoint(ctx: JobContext):
    # ──────────────────────────────────────────────────────────────
    # Outbound call logic (Twilio via LiveKit SIP)
    # ──────────────────────────────────────────────────────────────
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
                    wait_until_answered=True,          # waits until they pick up
                )
            )
            print(f"✅ Outbound call to {phone_number} connected!")
            await ctx.wait_for_participant(identity=phone_number)

        except api.TwirpError as e:                    # ✅ better error handling
            print(f"❌ SIP call failed: {e.message}")
            print(f"   SIP status code: {e.metadata.get('sip_status_code')}")
            print(f"   SIP status: {e.metadata.get('sip_status')}")
            # ctx.shutdown()   # uncomment if you want to stop on failure

    # ──────────────────────────────────────────────────────────────
    # Original agent setup (unchanged)
    # ──────────────────────────────────────────────────────────────
    graph = build_graph()

    session = AgentSession(
        llm=langchain.LLMAdapter(graph=graph),
        stt=deepgram.STT(model="nova-2"),
        tts=deepgram.TTS(),
        vad=silero.VAD.load(),
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