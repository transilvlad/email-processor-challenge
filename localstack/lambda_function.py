import json
import os
from datetime import datetime

import boto3
from botocore.config import Config


# Lambda handler for SQS events
def lambda_handler(event, context):
    db_url = os.environ.get('LOCALSTACK_URL')

    for message in event['Records']:
        print("event record", message)

        client = boto3.client(
            's3',
            endpoint_url=db_url,
            aws_access_key_id="local",
            aws_secret_access_key="local",
            config=Config(
                retries={'max_attempts': 3, 'mode': 'standard'}
            )
        )

        data = json.loads(message)

        item = {
            'message_id': data["message_id"],
            'subject': data["subject"],
            'sender': data["sender"],
            'recipient': data["recipient"],
            'timestamp': datetime.now().isoformat()
        }

        response = client.put_item(TableName='ProcessedEmails',
                                   Item=item)

        print("db response", response)
