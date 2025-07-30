Email Processor Challenge
==

This application sets up KumoMTA container to post inbound messages to a FastAPI container
which in turn takes the RAW email and puts it in S3 and the metadata and queues it in SQS
only to be picked up by a lambda function which inserts the metadata into DynamoDB.

How to test
--

```commandline
docker compose up
```

Send an email with your favorite client to localhost:25 addressed to anyone @example.com.

Wait for the email to process

```commandline
docker compose exec localstack bash
```

This logs into the localstack container where you can query the DB

```commandline
awslocal dynamodb scan --endpoint-url http://localhost:4566 --region us-east-1 --table-name ProcessedEmails --output table
```

If I got the insert to work you should see an entry,
otherwise you can run `lambda_function_test.py` to make a call that will insert an entry you can query.

Disclosure
--

- My first Docker compose and AWS project.
- Learning is a stressful adventure when pressed by time.
- I know OOP, but time wasn't on my side.
