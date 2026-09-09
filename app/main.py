from fastapi import FastAPI

from app.api.routes_chat import router as chat_router, set_pipeline
from app.api.routes_health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.embeddings.embedder import BgeM3Embedder
from app.rag.generator import DeterministicGenerator, OpenAICompatibleGenerator
from app.rag.pipeline import RagPipeline
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import FaissVectorStore


configure_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

if (settings.vector_index_dir / "index.faiss").exists() and (settings.vector_index_dir / "metadata.json").exists():
	embedder = BgeM3Embedder(settings.embedding_model, settings.embedding_batch_size, settings.embedding_device)
	retriever = Retriever(
		FaissVectorStore.load(settings.vector_index_dir),
		embedder,
		top_k=settings.top_k,
		threshold=settings.similarity_threshold,
	)
	generator = OpenAICompatibleGenerator(settings) if settings.llm_api_key and settings.llm_model else DeterministicGenerator()
	set_pipeline(RagPipeline(retriever, generator))

app.include_router(health_router)
app.include_router(chat_router)
