#!/bin/sh

# Change to the application directory.
cd /app || exit

echo "Initializing localstack"

# Wait for LocalStack to be fully ready before executing AWS CLI commands.
sleep 5

# --- S3 Configuration ---
# Create an S3 bucket to store email attachments.
awslocal s3 mb s3://email-attachments

# --- SQS Configuration ---
# Create a standard SQS queue for processing incoming emails.
awslocal sqs create-queue --queue-name email-processing

# --- Lambda Configuration ---
# Package the Python script into a zip file for the Lambda function.
zip lambda_function.zip lambda_function.py

# Create a Lambda function named 'email-processor'.
# It uses Python 3.13, and the code is from the zipped package.
awslocal lambda create-function \
            --function-name email-processor \
            --runtime python3.13 \
            --zip-file fileb://lambda_function.zip \
            --handler lambda_function.lambda_handler \
            --role arn:aws:iam::000000000000:role/lambda-role \
            --environment Variables="{`cat .env | xargs | sed 's/ /,/g'`}"

# Create a mapping between the SQS queue and the Lambda function.
# This configures the Lambda function to be triggered by messages in the 'email-processing' SQS queue.
awslocal lambda create-event-source-mapping \
            --function-name email-processor \
            --batch-size 5 \
            --maximum-batching-window-in-seconds 60  \
            --event-source-arn arn:aws:sqs:${AWS_DEFAULT_REGION}:000000000000:email-processing \
            --endpoint-url http://localhost:4566 \
            --region ${AWS_DEFAULT_REGION}


# --- DynamoDB Configuration ---
# Create a DynamoDB table to store processed email metadata.
# The keys used are message_id and recipient.
# This allows for efficient lookups of specific emails sent to each recipient while avoiding duplicate entries for the same email.
awslocal dynamodb create-table \
    --endpoint-url http://localhost:4566 \
    --region ${AWS_DEFAULT_REGION} \
    --table-name ProcessedEmails \
    --attribute-definitions \
        AttributeName=message_id,AttributeType=S \
        AttributeName=recipient,AttributeType=S \
    --key-schema \
        AttributeName=message_id,KeyType=HASH \
        AttributeName=recipient,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=LocalStack Key=Purpose,Value=EmailStorage

# Wait for the DynamoDB table to become active before other services try to access it.
aws dynamodb wait table-exists \
    --endpoint-url http://localhost:4566 \
    --region ${AWS_DEFAULT_REGION} \
    --table-name ProcessedEmails

echo "Localstack initialized"
