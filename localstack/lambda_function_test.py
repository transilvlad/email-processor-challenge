import json

from localstack.lambda_function import lambda_handler

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
