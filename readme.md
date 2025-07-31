Email Processor Challenge
==

This application sets up KumoMTA container to post inbound messages to a FastAPI container
which in turn takes the RAW email and puts it in S3 and the metadata and queues it in SQS
only to be picked up by a lambda function which inserts the metadata into DynamoDB.

How to test
--

- Run:
```commandline
docker compose up
```

Send an email with your favorite client to `localhost:25` addressed to anyone `@example.com`.
You can send the email to multiple recipients as well.

Wait for the email to process. You can watch the localstack container logs to see the process work.

For example when an email with two recipients is received the logs will show:

```pycon
AWS s3.PutObject => 200
AWS s3.PutObject => 200
AWS sqs.SendMessage => 200
AWS sqs.SendMessage => 200
AWS dynamodb.PutItem => 200
AWS dynamodb.PutItem => 200
```

This demonstrates that when KumoMTA receives the email and pings FastAPI once for each recipient
which then stores the email twice in S3 using a key derived by concatenating the Message-ID and Recipient address.

Then it queues two SQS messages with the metadata of each recipient.

SQS will trigger the lambda function which inserts the data in DynamoDB.

To check the database run:
```commandline
docker compose exec localstack bash
```

This logs into the localstack container where you can query the DB with:
```commandline
awslocal dynamodb scan --endpoint-url http://localhost:4566 --region us-east-1 --table-name ProcessedEmails
```

You should see an entry for each message recipient combination like this:

```json
{
  "Items": [
    {
      "sender": {
        "S": "robin@transilvlad.net"
      },
      "subject": {
        "S": "Lipsum"
      },
      "domain": {
        "S": "example.com"
      },
      "recipient": {
        "S": "lady@example.com"
      },
      "created_at": {
        "N": "1753959198"
      },
      "processed_at": {
        "S": "2025-07-31T10:53:18.382667+00:00"
      },
      "message_id": {
        "S": "<10edbace-9dd2-4335-a978-47159a2d3c8a-1753959157566robin@transilvlad.net>"
      },
      "timestamp": {
        "S": "2025-07-31T10:52:37"
      }
    },
    {
      "sender": {
        "S": "robin@transilvlad.net"
      },
      "subject": {
        "S": "Lipsum"
      },
      "domain": {
        "S": "example.com"
      },
      "recipient": {
        "S": "robin@example.com"
      },
      "created_at": {
        "N": "1753959198"
      },
      "processed_at": {
        "S": "2025-07-31T10:53:18.274790+00:00"
      },
      "message_id": {
        "S": "<10edbace-9dd2-4335-a978-47159a2d3c8a-1753959157566robin@transilvlad.net>"
      },
      "timestamp": {
        "S": "2025-07-31T10:52:37"
      }
    }
  ],
  "Count": 2,
  "ScannedCount": 2,
  "ConsumedCapacity": null
}
```

Disclosure
--

- My first Docker compose and AWS project.
- Learning is a messy adventure under time pressure.
- I know and love OOP, I'm just rusty in Python :)
