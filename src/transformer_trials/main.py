import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig
from typing import Annotated

import click
from sqlmodel import SQLModel, Session, create_engine
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from .logger import LOGGING_CONFIG, CustomLogger
from .models import User

logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("my_logger")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"





@click.group()
def cli():
    load_dotenv()
    logger.info("Starting server...")


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    def get_session():
        with Session(engine) as session:
            yield session
    SessionDep = Annotated[Session, Depends(get_session)]
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
@click.option('-v', '--verbose', count=True, default=0)
def serve(port: int, host: str, verbose:int):
    match verbose:
        case 0:
            logger.setLevel(logging.CRITICAL)
        case 1:
            logger.setLevel(logging.ERROR)
        case 2:
            logger.setLevel(logging.WARNING)
        case 3:
            logger.setLevel(logging.INFO)
        case 4:
            logger.setLevel(logging.DEBUG)
        case _:
            logger.setLevel(logging.INFO)

    uvicorn.run(api, host=host, port=port, log_config=LOGGING_CONFIG, log_level=logging.getLevelName(logger.getEffectiveLevel()).lower())


if __name__ == "__main__":
    cli()
