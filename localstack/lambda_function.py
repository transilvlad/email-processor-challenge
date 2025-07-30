import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource (high-level API - recommended)
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('LOCALSTACK_URL', 'http://localhost:4566'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')
)

table_name = os.environ.get('DYNAMODB_TABLE', 'ProcessedEmails')
table = dynamodb.Table(table_name)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Processing {len(event.get('Records', []))} email messages")

    successful_messages = []
    failed_messages = []

    for record in event.get('Records', []):
        try:
            # Parse the SQS message body
            message_body = json.loads(record['body'])
            message_id = record.get('messageId')

            logger.info(f"Processing message {message_id}: {message_body}")

            # Extract email data from the message
            email_data = extract_email_data(message_body)

            # Store email in DynamoDB using resource API
            store_email_in_dynamodb(email_data)

            successful_messages.append({
                'messageId': message_id,
                'email_message_id': email_data['message_id']
            })

            logger.info(f"Successfully processed message {message_id}")

        except Exception as e:
            logger.error(f"Error processing message {record.get('messageId')}: {str(e)}")
            failed_messages.append({
                'messageId': record.get('messageId'),
                'error': str(e),
                'body': record.get('body', '')
            })

    # Return processing results
    result = {
        'statusCode': 200,
        'successful_count': len(successful_messages),
        'failed_count': len(failed_messages),
        'successful_messages': successful_messages,
        'failed_messages': failed_messages
    }

    if failed_messages:
        logger.warning(f"Failed to process {len(failed_messages)} messages")
        # For partial failures, let successful messages be deleted
        if len(failed_messages) == len(event.get('Records', [])):
            raise Exception(f"All {len(failed_messages)} messages failed processing")

    logger.info(f"Processing complete: {result}")
    return result


def extract_email_data(message_body: Dict[str, Any]) -> Dict[str, Any]:
    # Extract required fields
    sender = message_body.get('sender')
    recipient = message_body.get('recipient')
    subject = message_body.get('subject', '')
    message_id = message_body.get('message_id')
    timestamp = message_body.get('timestamp')

    # Validate required fields
    if not sender:
        raise ValueError("Missing required field: sender")
    if not recipient:
        raise ValueError("Missing required field: recipient")
    if not message_id:
        raise ValueError("Missing required field: message_id")

    # Create normalized timestamp
    if timestamp:
        try:
            dt = datetime.fromtimestamp(float(timestamp))
            iso_timestamp = dt.isoformat()
        except (ValueError, TypeError):
            iso_timestamp = datetime.utcnow().isoformat()
    else:
        iso_timestamp = datetime.utcnow().isoformat()

    return {
        'message_id': str(message_id),
        'sender': str(sender),
        'recipient': str(recipient),
        'subject': str(subject),
        'timestamp': iso_timestamp,
        'created_at': int(datetime.utcnow().timestamp()),
        'raw_message': message_body.get('raw_message', ''),
        'domain': message_body.get('domain', ''),
        'processed_at': datetime.utcnow().isoformat()
    }


def store_email_in_dynamodb(email_data: Dict[str, Any]) -> None:
    try:
        # Store the email data using resource API (automatically handles type conversion)
        table.put_item(Item=email_data)
        logger.info(f"Stored email in DynamoDB: {email_data['message_id']}")

    except Exception as e:
        logger.error(f"Failed to store email in DynamoDB: {str(e)}")
        raise


# For local testing
if __name__ == "__main__":
    # Sample test event
    test_event = {
        "Records": [
            {
                "messageId": "test-message-id",
                "body": json.dumps({
                    "sender": "robin@transilvlad.net",
                    "recipient": "robin@example.com",
                    "raw_message": "",
                    "domain": "example.com",
                    "subject": "Lipsum",
                    "message_id": "<c530b14d-4d3f-49e3-a931-2341465bab12-1753885206019robin@transilvlad.net>",
                    "timestamp": 1753885206.0
                })
            }
        ]
    }


    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"


    try:
        result = lambda_handler(test_event, MockContext())
        print("✅ Test passed!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
