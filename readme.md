Email Processor Challenge
==

This application sets up KumoMTA container to post inbound messages to a FastAPI container
which in turn takes the RAW email and puts it in S3 and then queues the metadata in SQS for processing
via a lambda function which inserts the metadata into DynamoDB.


How to
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

Development process
--
In the development of this application I used `requestcatcher.com` to validate the API calls up to SQS.

1. Add container for KumoMTA and configure to POST messages to the sandbox first while also learning lua scripting.
2. Add container for FastAPI and configure to receive the POST from KumoMTA and post it to the sandbox.
3. Add container for localstack and implement S3 upload and SQS queueing in FastAPI.
4. Write lambda function and test with an SQS mock payload using a test script and double check results in DynamoDB.
5. Create lambda function and event source mapping and fight the gods of environment variables.

Sending emails to KumoMTA can be done in many ways but me personally I used [Robin](https://github.com/mimecast/robin).
Robin is designed for end to end MTA testing using JSON5 case files, this is the one I used:

```json5
{
  $schema: "/schema/case.schema.json",
  // Route.
  mx: [
    "localhost"
  ],
  port: 25,
  // Disable TLS.
  tls: false,
  // EHLO domain.
  ehlo: "transilvlad.net",
  // Email envelopes.
  envelopes: [
    // Envelope one.
    {
      // Envelope sender.
      mail: "vlad@transilvlad.net",
      // Envelope recipients.
      rcpt: [
        "robin@example.com",
        "lady@example.com"
      ],
      // Email eml file to transmit.
      file: "src/test/resources/cases/sources/lipsum.eml",
      // Assertions to run against the envelope.
      assertions: {
        // Protocol assertions.
        // Check SMTP responses match regular expressions.
        protocol: [
          [
            "MAIL",
            "250 OK"
          ],
          [
            "RCPT",
            "250 OK"
          ],
          [
            "DATA",
            "250 OK"
          ]
        ]
      }
    }
  ],
  // Assertions to run against the connection.
  assertions: {
    // Protocol assertions.
    // Check SMTP responses match regular expressions.
    protocol: [
      [
        "SMTP",
        "^220"
      ],
      [
        "EHLO",
        "STARTTLS"
      ],
      [
        "QUIT"
      ]
    ]
  }
}
```

I ran it just like in this Robin example case:
https://github.com/mimecast/robin/blob/master/src/test/java/cases/ExampleSend.java


Disclosure
--

- My first Docker compose and AWS project.
- Learning is a messy adventure under time pressure.
- I haven't used Python in years.
- I learnt more in the last 3 days than in the last year :D
- [The obstacle is the way](https://en.wikipedia.org/wiki/The_Obstacle_Is_the_Way)
