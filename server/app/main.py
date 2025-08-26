from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router
from app.core.db import create_async_engine, create_async_sessionmaker
from app.core.document_loader import load_documents
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore

if __name__ == "__main__":
    chunks = load_documents("data")
    texts = [chunk["text"] for chunk in chunks]

    embedder = Embedder()
    embeddings = embedder.embed(texts)  # List[List[float]]
    embedded_chunks = [
        {
            "embedding": embedding,
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    vector_store: VectorStore = VectorStore()
    vector_store.add_embeddings(chunks, embeddings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine()
    sessionmaker = create_async_sessionmaker(engine)

    # yield dict → available in request.state
    yield {"db": sessionmaker}

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    origins = ["*"]

    app.include_router(router=router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
