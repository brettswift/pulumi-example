import logging
import os
import boto3
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Received event")
    logger.info(event)
    # Retrieve the message body from the event
    message_body = event['Records'][0]['body']

    # Log the message body
    logger.info(f"Received message: {message_body}")
    logger.info("Putting message into s3")
    # Call the function with the message body
    put_message_in_s3(message_body)

def put_message_in_s3(message_body):
    # Retrieve bucket name and prefix path from environment variables
    bucket_name = os.environ.get("BUCKET_NAME")
    prefix_path = os.environ.get("PREFIX_PATH")

    # Create a unique file name using current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    random_hash = os.urandom(4).hex()
    file_name = f"{prefix_path}/{timestamp}{random_hash}.txt"
    logger.info(f"writing file to: s3://{bucket_name}/{file_name}")
    # Create an S3 client
    s3_client = boto3.client("s3")

    # Put the message body into S3
    s3_client.put_object(Body=message_body, Bucket=bucket_name, Key=file_name)

    logger.info("Success")