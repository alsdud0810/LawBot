from collections.abc import Sequence

from app.retrieval.vector_store import SearchResult


REFUSAL_MESSAGES = {
    "ko": "현재 확보된 공식 자료만으로는 해당 질문에 대한 충분한 근거를 확인하기 어렵습니다. 필요한 경우 공식 기관이나 법률 전문가에게 상담받으세요.",
    "en": "I could not find sufficient support in the indexed official sources. Please consult an official agency or qualified legal professional when necessary.",
}


def has_sufficient_evidence(results: Sequence[SearchResult]) -> bool:
    return bool(results)


def refusal_message(language: str) -> str:
    return REFUSAL_MESSAGES.get(language, REFUSAL_MESSAGES["en"])
