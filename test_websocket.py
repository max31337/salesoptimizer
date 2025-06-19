#!/usr/bin/env python3
"""
WebSocket test client for SLA monitoring
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket():
    # You'll need to replace this with a valid JWT token from a super admin user
    # You can get this by logging in to the web app and checking the auth cookie
    token = input("Enter your JWT token (from browser cookies): ").strip()
    
    if not token:
        print("Token is required to test WebSocket authentication")
        return
    
    uri = f"ws://localhost:8000/api/v1/ws/sla-monitoring?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket at {uri}")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent: {ping_message}")
            
            # Listen for messages for 30 seconds
            print("🔄 Listening for messages (30 seconds)...")
            
            try:
                async with asyncio.timeout(30):
                    async for message in websocket:
                        data = json.loads(message)
                        print(f"📥 Received: {data['type']}")
                        
                        if data['type'] == 'pong':
                            print("   Pong received - connection is alive!")
                        elif data['type'] == 'sla_update':
                            health = data['data']['system_health']
                            alerts_count = len(data['data']['alerts'])
                            print(f"   System Status: {health['overall_status']}")
                            print(f"   Uptime: {health.get('uptime_percentage', 'N/A')}%")
                            print(f"   Active Alerts: {alerts_count}")
                        
                        # Request manual update after receiving first message
                        if data['type'] in ['pong', 'sla_update']:
                            print("📤 Requesting manual SLA update...")
                            await websocket.send(json.dumps({"type": "request_update"}))
                            
            except asyncio.TimeoutError:
                print("⏰ Timeout reached - ending test")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 SLA Monitoring WebSocket Test Client")
    print("=" * 50)
    asyncio.run(test_websocket())
