from time import time

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
    start = time()
    process(message)
    print("task time: ", time() - start)
    return message


# AWS URI's
s3_url = "http://localstack:4566"


# Upload message to S3 and queue in SQS
def process(message: Message):
    # Upload message to S3
    s3_upload(message)

    # TODO Queue in SQS


# S3 upload
def s3_upload(message: Message):
    # Initialize the S3 client with LocalStack endpoint
    s3_client = boto3.client(
        's3',
        endpoint_url=s3_url,
        aws_access_key_id="local",
        aws_secret_access_key="local",
        config=Config(
            retries={'max_attempts': 10, 'mode': 'standard'}
        )
    )

    response = s3_client.put_object(
        Body=message.raw_message,
        Bucket="email-attachments",
        Key=message.message_id + message.recipient,
    )

    print("s3 response: ", response)
