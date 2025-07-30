import asyncio
from time import time

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Message schema
class Message(BaseModel):
    sender: str
    recipient: str = None
    raw_message: str = None
    domain: str = None
    subject: str = None
    message_id: str = None
    timestamp: float


# Read POST requests from root and task for forwarding
@app.post("/")
async def read_root(message: Message):
    start = time()
    await task(message)
    print("task time: ", time() - start)
    return message


# Forward URL
url = "https://kumod.requestcatcher.com/"


# Async task
async def task(message: Message):
    async with httpx.AsyncClient() as client:
        await asyncio.gather(post(client, message))


# Async POST to forwarding URL
# TODO Upload to S3 and queue in SQS instead
async def post(client, message: Message):
    response = await client.post(url,
                                 headers={"Content-Type": "application/json"},
                                 data=message.model_dump_json(),
                                 )
    print("post response: ", response.text)
    return response.text
