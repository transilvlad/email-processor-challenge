import os

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

        response = client.put_item(TableName='ProcessedEmails',
                                   Item={'fruitName': {'S': 'Banana'}, 'key2': {'N': 'value2'}})

        print("db response", response)
