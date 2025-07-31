#!/bin/sh
cd /app || exit

echo "Initializing localstack"

# Wait for LocalStack to be fully ready
sleep 5

# Create S3 bucket
awslocal s3 mb s3://email-attachments

# Create SQS queue
awslocal sqs create-queue --queue-name email-processing

# Create lambda function, map to SQS queue and zip python script
zip lambda_function.zip lambda_function.py

awslocal lambda create-function \
            --function-name email-processor \
            --runtime python3.13 \
            --zip-file fileb://lambda_function.zip \
            --handler lambda_function.lambda_handler \
            --role arn:aws:iam::000000000000:role/lambda-role \
            --environment Variables="{`cat .env | xargs | sed 's/ /,/g'`}"

awslocal lambda create-event-source-mapping \
            --function-name email-processor \
            --batch-size 5 \
            --maximum-batching-window-in-seconds 60  \
            --event-source-arn arn:aws:sqs:${AWS_DEFAULT_REGION}:000000000000:email-processing \
            --endpoint-url http://localhost:4566 \
            --region ${AWS_DEFAULT_REGION}


# Create DynamoDB table for messages
awslocal dynamodb create-table \
    --endpoint-url http://localhost:4566 \
    --region ${AWS_DEFAULT_REGION} \
    --table-name ProcessedEmails \
    --attribute-definitions \
        AttributeName=message_id,AttributeType=S \
        AttributeName=sender,AttributeType=S \
    --key-schema \
        AttributeName=message_id,KeyType=HASH \
        AttributeName=sender,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=LocalStack Key=Purpose,Value=EmailStorage

# Wait for table to be active
aws dynamodb wait table-exists \
    --endpoint-url http://localhost:4566 \
    --region ${AWS_DEFAULT_REGION} \
    --table-name ProcessedEmails

echo "Localstack initialized"
