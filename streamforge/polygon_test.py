import asyncio
import websockets
import json
import logging

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURATION ---
# ⚠️ Replace this with your actual Polygon.io API key
API_KEY = "YOUR_API_KEY"

# Choose your endpoint:
# Real-Time: wss://socket.polygon.io/stocks
# Delayed (15 min): wss://delayed.polygon.io/stocks
WS_URL = "wss://socket.polygon.io/stocks"

# The topic to subscribe to. 'AM.*' is Aggregates Per Minute for all tickers.
SUBSCRIPTION_TOPIC = "AM.*"


# ---------------------

async def connect_and_stream():
    """Connects to the Polygon.io WebSocket and streams data."""
    try:
        # 1. Connect
        # The 'async with' statement automatically handles connection opening and closing.
        async with websockets.connect(WS_URL) as websocket:
            logging.info(f"Connected to {WS_URL}")

            # 2. Authenticate
            auth_message = {
                "action": "auth",
                "params": API_KEY
            }
            await websocket.send(json.dumps(auth_message))
            logging.info("Authentication message sent. Awaiting confirmation...")

            # Wait for the Auth confirmation message
            auth_response = await websocket.recv()
            logging.info(f"Auth Response: {auth_response}")

            # 3. Subscribe
            subscribe_message = {
                "action": "subscribe",
                "params": SUBSCRIPTION_TOPIC
            }
            await websocket.send(json.dumps(subscribe_message))
            logging.info(f"Subscription message sent for topic: {SUBSCRIPTION_TOPIC}")

            # 4. Receive and Process
            logging.info("Starting data reception loop...")
            async for message in websocket:
                data = json.loads(message)

                # Polygon sends a list of events. Iterate through them.
                for event in data:
                    event_type = event.get("ev")

                    # Handle control messages (e.g., status/subscription confirmation)
                    if event_type == "status":
                        logging.warning(f"Control Message: {event.get('message')}")
                        continue

                    # Process market data (Aggregates Per Minute event type is 'AM')
                    if event_type == "AM":
                        # The 'c' field is the closing price of the minute bar
                        # The 'v' field is the volume for that minute
                        logging.info(
                            f"[{event.get('sym')}] | Close: ${event.get('c'):<10} | Volume: {event.get('v'):,} | Time: {event.get('s')}")

                    # You can add logic for other event types (e.g., T for Trades, Q for Quotes)

    except websockets.exceptions.ConnectionClosedOK:
        logging.info("Connection closed gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Ensure you have the 'websockets' library installed: pip install websockets
    logging.info("Starting Polygon.io WebSocket connection script...")
    asyncio.run(connect_and_stream())