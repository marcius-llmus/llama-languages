from enum import StrEnum


class FeedbackType(StrEnum):
    CORRECTION = "correction"
    TIP = "tip"
    SUGGESTION = "suggestion"


class ConversationEventType(StrEnum):
    AI_TEXT_CHUNK_GENERATED = "ai_text_chunk_generated"
    AI_AUDIO_CHUNK_GENERATED = "ai_audio_chunk_generated"
    AI_AUDIO_READY = "ai_audio_ready"
    AUDIO_MESSAGE = "audio_message"
    USER_TRANSCRIPTION_CHUNK_GENERATED = "user_transcription_chunk_generated"
    FEEDBACK_GENERATED = "feedback_generated"