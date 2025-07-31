import os
from typing import Dict, Any

import boto3
from botocore.config import Config
from fastapi import FastAPI
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI()


class Message(BaseModel):
    """
    Pydantic model for an email message.
    """
    sender: str
    recipient: str | None = None
    raw_message: str | None = None
    domain: str | None = None
    subject: str | None = None
    message_id: str | None = None
    timestamp: float


class AWSManager:
    """
    A class to manage interactions with AWS services, specifically S3 and SQS.

    This class encapsulates the logic for uploading objects to S3 and queuing
    messages in SQS, promoting code reusability and separation of concerns.
    It uses environment variables for configuration.
    """

    def __init__(self):
        """Initializes the AWSManager with configurations from environment variables."""
        self.localstack_url = os.environ.get('LOCALSTACK_URL')
        self.sqs_queue_url = os.environ.get('SQSQUEUE_URL')
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_default_region = os.environ.get('AWS_DEFAULT_REGION')

    def s3_upload(self, message: Message) -> Dict[str, Any]:
        """
        Uploads the raw message content to an S3 bucket.

        Args:
            message: The Message object containing the raw message and metadata.
        """
        s3_client = boto3.client(
            's3',
            endpoint_url=self.localstack_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
        )

        try:
            response = s3_client.put_object(
                Body=message.raw_message,
                Bucket="email-attachments",
                Key=f"{message.message_id}-{message.recipient}"
            )
            print(f"S3 upload successful: {response}")

            return response

        except Exception as e:
            print(f"S3 upload failed: {e}")
            return {"error": True, "message": e}

    def sqs_queue(self, message: Message):
        """
        Queues the message metadata (without the raw message) into an SQS queue.

        Args:
            message: The Message object containing the metadata to be queued.
        """
        sqs_client = boto3.client(
            'sqs',
            endpoint_url=self.sqs_queue_url,
            region_name=self.aws_default_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        # Clear the raw message before queuing to save space and avoid sensitive data in queue
        message.raw_message = None

        try:
            response = sqs_client.send_message(
                QueueUrl=self.sqs_queue_url,
                MessageBody=message.model_dump_json()
            )
            print(f"SQS message queued successfully: {response}")
            return response

        except Exception as e:
            print(f"SQS queuing failed: {e}")
            return {"error": True, "message": e}


# Initialize AWSManager
aws_manager = AWSManager()


@app.post("/")
def process_message(message: Message):
    """
    Endpoint to receive and process a message.

    This function serves as the main entry point for the FastAPI application,
    triggering the upload to S3 and queuing in SQS.
    """
    aws_manager.s3_upload(message)
    aws_manager.sqs_queue(message)

    return {"status": "Message processed successfully"}
