from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router
from app.core.db import create_async_engine, create_async_sessionmaker
from app.core.memory_db import SQLiteKVStore
from app.core.config import settings
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.workers.tasks import file_update_consumer

from app.exception_handler import add_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine()
    sessionmaker = create_async_sessionmaker(engine)
    memory_db = SQLiteKVStore(memory=True)  # create once
    embedder = Embedder()
    vector_store = VectorStore(
        collection_name=settings.COLLECTION_NAME,
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
        auth_credentials=settings.CHROMA_AUTH_SECRET,
        token_header=settings.CHROMA_TOKEN_HEADER,
    )

    app.state.background_tasks = [asyncio.create_task(file_update_consumer())]

    # yield dict → available in request.state
    yield {
        "db": sessionmaker,
        "memory_db": memory_db,
        "embedder": embedder,
        "vector_store": vector_store,
    }

    for task in app.state.background_tasks:
        task.cancel()

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    origins = ["http://localhost:5173"]

    app.include_router(router=router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_exception_handlers(app)

    return app


app = create_app()
