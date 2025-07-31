import json
import os
from datetime import datetime, UTC
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


class EmailProcessor:
    """
    A class to handle the processing of SQS messages and storing them in DynamoDB.

    This class encapsulates the logic for interacting with AWS services,
    parsing email data from SQS messages, and writing to a DynamoDB table.
    """

    def __init__(self):
        """
        Initializes the EmailProcessor and establishes a connection to DynamoDB.
        """
        # Initialize DynamoDB resource using environment variables
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('LOCALSTACK_URL'),
            region_name=os.environ.get('AWS_DEFAULT_REGION'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        self.table = self.dynamodb.Table(os.environ.get('DYNAMODB_TABLE'))

    def _extract_email_data(self, message_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and validates email data from a parsed SQS message body.

        Args:
            message_body: The dictionary containing the email message data.

        Returns:
            A dictionary with the extracted and normalized email data.

        Raises:
            ValueError: If a required field (sender, recipient, or message_id) is missing.
        """
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
        iso_timestamp = self._normalize_timestamp(timestamp)

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

    def _normalize_timestamp(self, timestamp: Any) -> str:
        """
        Converts a timestamp into an ISO 8601 formatted string.

        Args:
            timestamp: The timestamp to convert, can be a float or string.

        Returns:
            A string representing the ISO 8601 timestamp.
        """
        if timestamp:
            try:
                dt = datetime.fromtimestamp(float(timestamp), UTC)
                return dt.isoformat()
            except (ValueError, TypeError):
                # Fallback to current time if timestamp is invalid
                pass
        return datetime.now(UTC).isoformat()

    def _store_email_in_dynamodb(self, email_data: Dict[str, Any]) -> None:
        """
        Stores the extracted email data in the configured DynamoDB table.

        Args:
            email_data: The dictionary of email data to be stored.

        Raises:
            ClientError: If the put_item operation fails.
        """
        try:
            # Store the email data using resource API
            self.table.put_item(Item=email_data)
            print(f"Stored email in DynamoDB: {email_data['message_id']}")
        except ClientError as e:
            print(f"Failed to store email in DynamoDB: {e.response['Error']['Message']}")
            raise

    def process_record(self, record: Dict[str, Any]) -> str:
        """
        Processes a single SQS message record.

        Args:
            record: A single record from the SQS event.

        Returns:
            The message_id of the processed email.
        """
        message_body = json.loads(record['body'])
        message_id = record.get('messageId')
        print(f"Processing message {message_id}: {message_body}")

        email_data = self._extract_email_data(message_body)
        print(f"Extracted email data {email_data}")

        self._store_email_in_dynamodb(email_data)

        print(f"Successfully processed message {message_id}")
        return email_data['message_id']


# Initialize the processor outside the handler for warm starts
processor = EmailProcessor()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.

    This function is the entry point for the Lambda, responsible for iterating
    through SQS records and delegating the processing to the EmailProcessor class.
    """
    print(f"Processing {len(event.get('Records', []))} email messages")

    successful_messages = []
    failed_messages = []

    for record in event.get('Records', []):
        try:
            email_message_id = processor.process_record(record)
            successful_messages.append({
                'messageId': record.get('messageId'),
                'email_message_id': email_message_id
            })
        except Exception as e:
            print(f"Error processing message {record.get('messageId')}: {e}")
            failed_messages.append({
                'messageId': record.get('messageId'),
                'error': str(e),
                'body': record.get('body', '')
            })

    result = {
        'statusCode': 200,
        'successful_count': len(successful_messages),
        'failed_count': len(failed_messages),
        'successful_messages': successful_messages,
        'failed_messages': failed_messages
    }

    if failed_messages:
        print(f"Failed to process {len(failed_messages)} messages")
        if len(failed_messages) == len(event.get('Records', [])):
            raise Exception(f"All {len(failed_messages)} messages failed processing")

    print(f"Processing complete: {result}")
    return result
