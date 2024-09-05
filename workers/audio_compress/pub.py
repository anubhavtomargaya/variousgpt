from google.cloud import pubsub_v1
import json

# Setup Pub/Sub Publisher
PROJECT_ID = 'your-project-id'  # Replace with your project ID
TOPIC_ID = 'process-updates'  # The topic you created

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def publish_update(stage, status):
    """Publish a message to Pub/Sub"""
    message_data = json.dumps({'stage': stage, 'status': status}).encode('utf-8')
    future = publisher.publish(topic_path, message_data)
    future.result()  # Block until the message is published
