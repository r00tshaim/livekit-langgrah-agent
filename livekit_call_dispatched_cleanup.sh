#!/bin/bash
# cleanup-dispatches.sh - Tiny cleanup tool for old dispatches (deletes rooms)

echo "📋 LiveKit Cleanup Tool"
echo "======================"
echo ""

echo "1. Current rooms (dispatches live inside these):"
lk room list
echo ""

echo "2. Tip: To see dispatches inside a room → lk dispatch list <room-name>"
echo ""

read -p "🔥 Enter exact room name to DELETE (or press Enter to cancel): " room_name

if [ -n "$room_name" ]; then
    read -p "⚠️  Delete room '$room_name' + ALL its dispatches? (y/N) " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        lk room delete "$room_name"
        echo "✅ Room '$room_name' and its dispatches deleted!"
    else
        echo "❌ Cancelled."
    fi
else
    echo "No action taken."
fi

echo ""
echo "Run this script again anytime to see the updated list."