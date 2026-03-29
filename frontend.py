import os
import uuid
from datetime import timedelta

import streamlit as st
from livekit.api import AccessToken, VideoGrants
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LiveKit Agent Demo", page_icon="🎙️")

st.title("LiveKit Agent Demo")
st.write("Generate a room token and open the LiveKit Agents Playground.")

livekit_url = st.text_input(
    "LiveKit URL",
    value=os.getenv("LIVEKIT_URL", ""),
    placeholder="wss://your-project.livekit.cloud",
)

api_key = st.text_input(
    "LiveKit API Key",
    value=os.getenv("LIVEKIT_API_KEY", ""),
)

api_secret = st.text_input(
    "LiveKit API Secret",
    value=os.getenv("LIVEKIT_API_SECRET", ""),
    type="password",
)

room_name = st.text_input("Room name", value="demo-room")
identity = st.text_input("Participant identity", value=f"user-{uuid.uuid4().hex[:8]}")

if st.button("Generate join token"):
    if not livekit_url or not api_key or not api_secret:
        st.error("Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET.")
        st.stop()

    token = (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_ttl(timedelta(hours=1))
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )

    st.success("Token generated.")
    st.code(token, language="text")

    st.link_button(
        "Open LiveKit Agents Playground",
        "https://agents-playground.livekit.io/",
    )

    st.caption(
        "Paste the LiveKit URL and token into the Playground to join the room."
    )