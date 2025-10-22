from enum import StrEnum


class ConversationEventType(StrEnum):
    TEXT_CHUNK = "text_chunk"
    AUDIO_READY = "audio_ready"