import asyncio
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from time import time

app = FastAPI()


class Item(BaseModel):
    sender: str
    recipient: str = None
    raw_message: str = None
    domain: str = None
    subject: str = None
    message_id: str = None
    timestamp: float


@app.post("/")
async def read_root(item: Item):
    start = time()
    await task(item)
    print("task time: ", time() - start)
    return item


url = "https://kumod.requestcatcher.com/"


async def task(item: Item):
    async with httpx.AsyncClient() as client:
        await asyncio.gather(post(client, item))


async def post(client, item: Item):
    response = await client.post(url,
                                 headers={"Content-Type": "application/json"},
                                 data=item.model_dump_json(),
                                 )
    print("post response: ", response.text)
    return response.text
