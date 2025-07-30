import json

from localstack.lambda_function import lambda_handler

# For local testing
if __name__ == "__main__":
    # Sample test event
    test_event = {
        "Records": [
            {
                "messageId": "test-message-id",
                "body": json.dumps(
                    {'sender': 'robin@transilvlad.net', 'recipient': 'robin@example.com', 'raw_message': '',
                     'domain': 'example.com', 'subject': 'Lipsum',
                     'message_id': '<557828a4-7624-41bc-9f4e-c3a83b5babfe-1753893239239robin@transilvlad.net>',
                     'timestamp': 1753893239.0})
            }
        ]
    }

    try:
        result = lambda_handler(test_event, None)
        print("✅ Test passed!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
