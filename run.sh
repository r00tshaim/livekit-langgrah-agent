#!/bin/bash

# Activate venv if needed
source .venv/bin/activate

echo "Starting LiveKit agent..."
uv run python -m agent.main dev &

AGENT_PID=$!

echo "Starting Streamlit..."
uv run streamlit run frontend.py &

STREAMLIT_PID=$!

echo "Agent PID: $AGENT_PID"
echo "Streamlit PID: $STREAMLIT_PID"

# Wait for both
wait