from llama_index.core.llms import ChatMessage
from workflows.events import Event


class PromptReady(Event):
    """Carries the fully constructed prompt and voice ID."""

    messages: list[ChatMessage]
    voice_id: str | None


class TextChunkGenerated(Event):
    """Event carrying a single token from the LLM's streaming response."""

    delta: str


class FullResponseGenerated(Event):
    """Event carrying the full, final text response from the LLM."""

    full_response: str
    voice_id: str


class AudioReady(Event):
    """Event carrying the URL to the generated audio file."""

    audio_url: str


class AudioGenerated(Event):
    """Carries the full response after audio has been generated."""

    full_response: str
