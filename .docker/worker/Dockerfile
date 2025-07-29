FROM python:3.13

WORKDIR /app

COPY ./.docker/worker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV SQSCONSUMER_QUEUENAME=email-processing

ENTRYPOINT python sqs_consumer.py
