from llama_index.core.llms import ChatMessage
from workflows.events import Event

from app.conversation.schemas import Feedback


class UserTranscriptionChunkGenerated(Event):
    """Event carrying a single token from the streaming transcription."""

    delta: str


class AudioInputReceived(Event):
    """Indicates that an audio message has been received and is ready for transcription streaming."""
    audio_bytes: bytes
    persona_id: int
    language_profile_id: int


class UserMessageReady(Event):
    """Indicates the user's message is processed (transcribed if needed) and ready for the LLM."""
    text: str
    persona_id: int
    language_profile_id: int


class TextFeedbackRequired(Event):
    """Event to trigger parallel feedback generation for a text message."""

    user_message_text: str
    persona_id: int
    language_profile_id: int


class AudioFeedbackRequired(Event):
    """Event to trigger parallel feedback generation for an audio message."""

    audio_bytes: bytes
    user_message_text: str
    persona_id: int
    language_profile_id: int


class PromptReady(Event):
    """Carries the fully constructed prompt and voice ID."""

    messages: list[ChatMessage]
    voice_id: str | None
    user_message_text: str
    persona_id: int
    language_profile_id: int


class FeedbackGenerated(Event):
    """Carries the feedback object for the user's last message."""

    feedbacks: list[Feedback]


class AITextChunkGenerated(Event):
    """Event carrying a single token from the LLM's streaming response."""

    delta: str


class FullResponseGenerated(Event):
    """Event carrying the full, final text response from the LLM and the generated audio."""

    ai_response_text: str
    user_message_text: str
    audio_bytes: bytes
    persona_id: int
    language_profile_id: int


class AIAudioSaved(Event):
    """Event carrying the URL to the generated audio file."""

    audio_url: str


class AIAudioChunkGenerated(Event):
    """Event carrying a chunk of generated audio data."""

    chunk: bytes