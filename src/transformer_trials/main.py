import asyncio
import logging
from contextlib import asynccontextmanager

import click
import hypercorn
import uvloop
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from hypercorn.asyncio import serve as hypercorn_serve
from hypercorn.config import Config
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from .logger import LogHijack, get_logger

logger = get_logger(logging.DEBUG)

config: Config

class CustomConfig(Config):
    def __init__(self):
        self.logger_class = logging.Logger
        super().__init__()

@click.group()
def cli():
    global config
    config = CustomConfig()
    load_dotenv()
    logger.info("Starting server...")


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)

@app.event("app_mention")
async def handle_app_mentions(body, say):
    logger.debug(body)
    await say("What's up?")


@app.event("message")
async def handle_message():
    pass

api = FastAPI(lifespan=lifespan)

@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@cli.command()
@click.option(
    "--reload", "-r", is_flag=True, help="If specified, server will auto reload."
)
@click.option(
    "--port",
    "-p",
    default=8000,
    help="Port on which to serve the API. Defaults to 8000.",
)
@click.option(
    "--host",
    "-i",
    default="127.0.0.1",
    help="IP address on which to bind the server. Defaults to 127.0.0.1.",
)
def serve(reload: bool, port: int, host: str):
    # uvloop.install()
    asyncio.run(hypercorn_serve(app=api, config=config)) # type: ignore


if __name__ == "__main__":
    cli()
