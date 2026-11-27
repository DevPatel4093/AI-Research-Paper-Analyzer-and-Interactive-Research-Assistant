class ResearchAIError(Exception):
    """Base exception with a user-safe message."""


class ValidationError(ResearchAIError):
    pass


class ExtractionError(ResearchAIError):
    pass


class EmbeddingError(ResearchAIError):
    pass


class VectorStoreError(ResearchAIError):
    pass


class LLMError(ResearchAIError):
    pass
