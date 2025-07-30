import os

import boto3
from botocore.config import Config
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Message schema
class Message(BaseModel):
    sender: str
    recipient: str = None
    raw_message: str = None
    domain: str = None
    subject: str = None
    message_id: str = None
    timestamp: float


# Read POST requests from root and task for forwarding
@app.post("/")
def read_root(message: Message):
    process(message)


# AWS URI's
s3_url = os.environ.get('LOCALSTACK_URL')
sqs_url = os.environ.get('SQSQUEUE_URL')


# Upload message to S3 and queue in SQS
def process(message: Message):
    # Upload message to S3
    s3_upload(message)

    # Queue in SQS
    sqs_queue(message)


# S3 upload
def s3_upload(message: Message):
    # Initialize the S3 client with LocalStack endpoint
    client = boto3.client(
        's3',
        endpoint_url=s3_url,
        aws_access_key_id="local",
        aws_secret_access_key="local",
        config=Config(
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
    )

    response = client.put_object(
        Body=message.raw_message,
        Bucket="email-attachments",
        Key=message.message_id + message.recipient,
    )

    print("s3 response: ", response)


# SQS Queue
def sqs_queue(message: Message):
    client = boto3.client(
        'sqs',
        endpoint_url=sqs_url,
        region_name='us-east-1',
        aws_access_key_id="local",
        aws_secret_access_key="local"
    )
    message.raw_message = ""  # Clear RAW message, queue meta only
    response = client.send_message(
        QueueUrl=sqs_url,
        MessageBody=message.model_dump_json()
    )

    print("sqs response: ", response)
