#pip install google-cloud-pubsub

import json
from flask_socketio import SocketIO, emit
from google.cloud import pubsub_v1
import json
socketio = SocketIO(app)

# Setup Pub/Sub Publisher
PROJECT_ID = 'gmailapi-test-361320'  # Replace with your project ID
TOPIC_ID = 'process-updates'  # The topic you created

SUBSCRIPTION_ID = 'process-status'  # Replace with your subscription ID
def callback(message):
    """Callback function triggered when a message is received from Pub/Sub"""
    data = json.loads(message.data.decode('utf-8'))

    # Emit the progress update to connected WebSocket clients
    socketio.emit('progress', data)

    # Acknowledge the message (remove it from the Pub/Sub queue)
    message.ack()

def listen_to_pubsub():
    """Start listening to the Pub/Sub subscription"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Keep the subscription active
    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as e:
            print(f'Listening for Pub/Sub messages failed: {e}')
