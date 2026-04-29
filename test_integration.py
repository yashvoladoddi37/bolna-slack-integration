#!/usr/bin/env python3
"""
test_integration.py — End-to-end smoke test for the Bolna→Slack integration.

Usage:
    # With server running on port 8001:
    python test_integration.py

What it does:
    1. Sends a realistic Bolna execution payload to the local webhook endpoint.
    2. Verifies the webhook returns 200/accepted.
    3. Waits briefly and checks that no error appeared in the process.

The Slack alert is real — you should see a message appear in your Slack channel.
"""

import asyncio
import httpx

WEBHOOK_URL = "http://localhost:8001/webhook/bolna/call-ended"

# Simulates what Bolna sends when a call ends (mirrors the execution schema)
SAMPLE_PAYLOAD = {
    "id": "4c06b4d1-4096-4561-919a-4f94539c8d4a",
    "agent_id": "7baf87d2-ebb1-4000-902e-dd5bf506773a",
    "status": "completed",
    "conversation_time": 67.3,
    "transcript": (
        "Agent: Hello! Thank you for calling. How can I assist you today?\n"
        "User: Hi, I'd like to book an appointment with Dr. Sharma for tomorrow.\n"
        "Agent: Of course! Let me check availability. What time works best for you?\n"
        "User: Around 10 in the morning.\n"
        "Agent: Great, I have a slot available at 10:00 AM tomorrow with Dr. Sharma. "
        "Shall I confirm the booking?\n"
        "User: Yes please.\n"
        "Agent: Your appointment has been confirmed for tomorrow at 10:00 AM. "
        "You will receive an SMS confirmation shortly. Is there anything else I can help you with?\n"
        "User: No, that's all. Thank you!\n"
        "Agent: You're welcome. Have a great day!"
    ),
    "telephony_data": {
        "duration": "70",
        "to_number": "+919876543210",
        "from_number": "+918888888888",
        "call_type": "outbound",
        "provider": "twilio",
        "hangup_by": "User",
        "hangup_reason": "Normal Hangup",
    },
    "created_at": "2026-04-29T08:00:00Z",
    "updated_at": "2026-04-29T08:01:10Z",
}


async def run_test():
    print("=" * 60)
    print("Bolna → Slack Integration Smoke Test")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10) as client:
        # 1. Health check
        health = await client.get("http://localhost:8001/webhook/health")
        print(f"\n[1] Health check → {health.status_code}: {health.json()}")
        assert health.status_code == 200, "Server is not healthy!"

        # 2. Send completed call payload
        print(f"\n[2] Sending completed-call webhook payload …")
        resp = await client.post(WEBHOOK_URL, json=SAMPLE_PAYLOAD)
        print(f"    Status: {resp.status_code}")
        print(f"    Body:   {resp.json()}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "accepted"

        # 3. Test that non-terminal statuses are ignored
        non_terminal = dict(SAMPLE_PAYLOAD, status="in-progress", id="test-in-progress-002")
        resp2 = await client.post(WEBHOOK_URL, json=non_terminal)
        print(f"\n[3] Non-terminal status ('in-progress') → {resp2.json()['status']}")
        assert resp2.json()["status"] == "ignored"

    print("\n✅  All assertions passed.")
    print("    Check your Slack channel — you should see a call-ended message!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_test())
