from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router
from app.core.db import create_async_engine, create_async_sessionmaker
from app.core.memory_db import SQLiteKVStore
from app.core.config import settings

from app.core.embedder import Embedder
from app.core.vector_store import VectorStore

from app.exception_handler import add_exception_handlers

#     chunks = load_documents("data")
#     texts = [chunk["text"] for chunk in chunks]
#
#     embedder = Embedder()
#     embeddings = embedder.embed(texts)  # List[List[float]]
#     embedded_chunks = [
#         {
#             "embedding": embedding,
#             "text": chunk["text"],
#             "source": chunk["source"],
#             "chunk_id": chunk["chunk_id"],
#         }
#         for chunk, embedding in zip(chunks, embeddings)
#     ]
#
#     vector_store: VectorStore = VectorStore()
#     vector_store.add_embeddings(chunks, embeddings)
#


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

    # yield dict → available in request.state
    yield {
        "db": sessionmaker,
        "memory_db": memory_db,
        "embedder": embedder,
        "vector_store": vector_store,
    }

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    origins = ["http://localhost:5174"]

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
