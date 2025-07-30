import json


def lambda_handler(event, context):
    print(event, context)
    return {
        'statusCode': 200,
        'body': json.dumps('handling')
    }
