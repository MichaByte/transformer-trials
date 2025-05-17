import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from .logger import get_logger

logger = get_logger(logging.DEBUG)

load_dotenv()

app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say):
    logger.debug(body)
    await say("What's up?")


@app.event("message")
async def handle_message():
    pass


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


api = FastAPI(lifespan=lifespan)

@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)
