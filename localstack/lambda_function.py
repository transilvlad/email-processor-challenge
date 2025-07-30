def lambda_handler(event, context):
    for message in event['Records']:
        print(message)
