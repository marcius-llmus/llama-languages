from llama_index.core.llms import ChatMessage
from workflows.events import Event

from app.conversation.schemas import Feedback


class UserTranscriptionChunkGenerated(Event):
    """Event carrying a single token from the streaming transcription."""

    delta: str


class BaseConversationEvent(Event):
    """Base event carrying common contextual IDs for a conversation turn."""
    persona_id: int
    language_profile_id: int
    practice_topic_id: int | None


class AudioInputReceived(BaseConversationEvent):
    """Indicates that an audio message has been received and is ready for transcription streaming."""
    audio_bytes: bytes


class UserMessageReady(BaseConversationEvent):
    """Indicates the user's message is processed (transcribed if needed) and ready for the LLM."""
    text: str


class TextFeedbackRequired(BaseConversationEvent):
    """Event to trigger parallel feedback generation for a text message."""

    user_message_text: str


class AudioFeedbackRequired(BaseConversationEvent):
    """Event to trigger parallel feedback generation for an audio message."""

    audio_bytes: bytes
    user_message_text: str


class PromptReady(BaseConversationEvent):
    """Carries the fully constructed prompt and voice ID."""

    messages: list[ChatMessage]
    voice_id: str | None
    user_message_text: str


class FeedbackGenerated(Event):
    """Carries the feedback object for the user's last message."""

    feedbacks: list[Feedback]


class AITextChunkGenerated(Event):
    """Event carrying a single token from the LLM's streaming response."""

    delta: str


class FullResponseGenerated(BaseConversationEvent):
    """Event carrying the full, final text response from the LLM and the generated audio."""

    ai_response_text: str
    user_message_text: str
    audio_bytes: bytes


class AIAudioSaved(Event):
    """Event carrying the URL to the generated audio file."""

    audio_url: str


class AIAudioChunkGenerated(Event):
    """Event carrying a chunk of generated audio data."""

    chunk: bytes