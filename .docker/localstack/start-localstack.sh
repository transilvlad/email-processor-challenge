#!/bin/sh
echo "Initializing localstack"

awslocal s3 mb s3://email-attachments
awslocal sqs create-queue --queue-name email-processing
#awslocal dynamodb create-table \
#             --table-name received \
#             --attribute-definitions \
#                 AttributeName=Subject,AttributeType=S \
#                 AttributeName=MessageID,AttributeType=S \
#                 AttributeName=Sender,AttributeType=S \
#                 AttributeName=Recipient,AttributeType=S \
#             --key-schema AttributeName=Subject,KeyType=HASH AttributeName=MessageID,KeyType=RANGE \
#             --billing-mode PAY_PER_REQUEST \
#             --table-class STANDARD
