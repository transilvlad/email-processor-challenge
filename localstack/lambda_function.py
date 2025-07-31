import json
import os
from datetime import datetime, UTC
from typing import Dict, Any

import boto3

# Initialize DynamoDB resource (high-level API - recommended)
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('LOCALSTACK_URL'),
    region_name=os.environ.get('AWS_DEFAULT_REGION'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE'))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print(f"Processing {len(event.get('Records', []))} email messages")

    successful_messages = []
    failed_messages = []

    for record in event.get('Records', []):
        try:
            # Parse the SQS message body
            message_body = json.loads(record['body'])
            message_id = record.get('messageId')

            print(f"Processing message {message_id}: {message_body}")

            # Extract email data from the message
            email_data = extract_email_data(message_body)
            print(f"Extracted email data {email_data}")

            # Store email in DynamoDB using resource API
            store_email_in_dynamodb(email_data)

            successful_messages.append({
                'messageId': message_id,
                'email_message_id': email_data['message_id']
            })

            print(f"Successfully processed message {message_id}")

        except Exception as e:
            print(f"Error processing message {record.get('messageId')}: {str(e)}")
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
        print(f"Failed to process {len(failed_messages)} messages")
        # For partial failures, let successful messages be deleted
        if len(failed_messages) == len(event.get('Records', [])):
            raise Exception(f"All {len(failed_messages)} messages failed processing")

    print(f"Processing complete: {result}")
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
            iso_timestamp = datetime.now(UTC).isoformat()
    else:
        iso_timestamp = datetime.now(UTC).isoformat()

    return {
        'message_id': str(message_id),
        'sender': str(sender),
        'recipient': str(recipient),
        'subject': str(subject),
        'timestamp': iso_timestamp,
        'created_at': int(datetime.now(UTC).timestamp()),
        'domain': message_body.get('domain', ''),
        'processed_at': datetime.now(UTC).isoformat()
    }


def store_email_in_dynamodb(email_data: Dict[str, Any]) -> None:
    try:
        # Store the email data using resource API (automatically handles type conversion)
        table.put_item(Item=email_data)
        print(f"Stored email in DynamoDB: {email_data['message_id']}")

    except Exception as e:
        print(f"Failed to store email in DynamoDB: {str(e)}")
        raise
