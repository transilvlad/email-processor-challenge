import json
import os
from pathlib import Path

from dotenv import load_dotenv

# For local testing
if __name__ == "__main__":
    # Load environment variables
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)
    # Override localstack URL for localhost use
    os.environ["LOCALSTACK_URL"] = "http://localhost:4566"

    # Sample test event
    test_event = {
        'Records': [
            {
                'messageId': '7cdb2a87-7578-490e-b62f-c1a0c50d6238',
                'receiptHandle': 'OTA3NjNhOTAtZDZkOC00YzA1LTk5ODAtOWRkNjcyZGY1YTNmIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6ZW1haWwtcHJvY2Vzc2luZyA3Y2RiMmE4Ny03NTc4LTQ5MGUtYjYyZi1jMWEwYzUwZDYyMzggMTc1Mzg4NTQ4Ny42OTg3MDY=',
                'body': '{"sender": "robin@transilvlad.net", "recipient": "lady@example.com", "raw_message": "", "domain": "example.com", "subject": "Lipsum", "message_id": "<0eb7620e-131a-46f9-ac2b-305ee9e3fce5-1753885487145robin@transilvlad.net>", "timestamp": 1753885487.0}',
                'attributes': {
                    'SenderId': '000000000000',
                    'SentTimestamp': '1753885487693',
                    'ApproximateReceiveCount': '1',
                    'ApproximateFirstReceiveTimestamp': '1753885487698'
                },
                'messageAttributes': {},
                'md5OfBody': '391f22a7ccff24ee6d5e9c6d795c33bc',
                'eventSourceARN': 'arn:aws:sqs:us-east-1:000000000000:email-processing',
                'eventSource': 'aws:sqs',
                'awsRegion': 'us-east-1'
            }
        ]
    }

    try:
        from localstack.lambda_function import lambda_handler

        result = lambda_handler(test_event, None)
        print("✅ Test passed!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
