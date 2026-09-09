from app.models.response import ChatResponse, RetrievalResponse, SourceResponse
from app.rag.generator import Generator
from app.rag.grounding import has_sufficient_evidence, refusal_message
from app.rag.prompt import build_prompt
from app.retrieval.retriever import Retriever


class RagPipeline:
    def __init__(self, retriever: Retriever | None, generator: Generator) -> None:
        self.retriever = retriever
        self.generator = generator

    def answer(self, question: str, language: str) -> ChatResponse:
        results = self.retriever.retrieve(question) if self.retriever else []
        max_score = max((result.score for result in results), default=None)
        if not has_sufficient_evidence(results):
            return ChatResponse(
                answer=refusal_message(language),
                language=language,
                sources=[],
                retrieval=RetrievalResponse(top_k=0, max_score=max_score),
            )

        context = "\n\n".join(f"[{result.metadata.get('document_title', 'Unknown')} {result.metadata.get('article') or ''}] {result.text}" for result in results)
        answer = self.generator.generate(build_prompt(question, language, context))
        sources = [
            SourceResponse(
                document=result.metadata.get("document_title", "Unknown"),
                article=result.metadata.get("article"),
                url=result.metadata.get("source_url"),
            )
            for result in results
        ]
        return ChatResponse(
            answer=answer,
            language=language,
            sources=sources,
            retrieval=RetrievalResponse(top_k=len(results), max_score=max_score),
        )
