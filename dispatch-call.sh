#!/bin/bash
# dispatch-call.sh - Simple outbound call dispatcher (fixed)

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: ./dispatch-call.sh \"+919825626005\""
    echo "Example: ./dispatch-call.sh \"+919825626005\""
    exit 1
fi

PHONE_NUMBER="$1"

echo "📞 Dispatching outbound call to $PHONE_NUMBER ..."

# Single line - impossible to break on copy-paste
lk dispatch create --new-room --agent-name voice-agent --metadata "{\"phone_number\": \"$PHONE_NUMBER\"}"

echo "✅ Dispatch created successfully!"