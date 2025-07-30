#!/bin/sh
cd /app || exit

echo "Initializing localstack"

awslocal s3 mb s3://email-attachments

awslocal sqs create-queue --queue-name email-processing

zip lambda_function.zip lambda_function.py

awslocal lambda create-function \
            --function-name email-processor \
            --runtime python3.13 \
            --zip-file fileb://lambda_function.zip \
            --handler lambda_function.lambda_handler \
            --role arn:aws:iam::000000000000:role/lambda-role

awslocal lambda create-event-source-mapping \
            --function-name email-processor \
            --batch-size 5 \
            --event-source-arn arn:aws:sqs:us-east-1:000000000000:email-processing \
            --region us-east-1

#awslocal dynamodb create-table \
#            --table-name received \
#            --attribute-definitions \
#                 AttributeName=Subject,AttributeType=S \
#                 AttributeName=MessageID,AttributeType=S \
#                 AttributeName=Sender,AttributeType=S \
#                 AttributeName=Recipient,AttributeType=S \
#            --key-schema AttributeName=Subject,KeyType=HASH AttributeName=MessageID,KeyType=RANGE \
#            --billing-mode PAY_PER_REQUEST \
#            --table-class STANDARD
