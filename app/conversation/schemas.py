from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.conversation.enums import FeedbackType

class Feedback(BaseModel):
    type: FeedbackType = Field(
        description="The type of feedback provided regarding the user's message. 'ok' means no feedback is needed."
    )
    reasoning: Optional[str] = Field(
        description="A concise explanation for the feedback, explaining the grammatical error or suggesting a better phrasing."
    )


class FeedbackResponse(BaseModel):
    feedback: list[Feedback] = Field(
        description="A list of feedback items on the user's last message."
    )


class WebSocketMessage(BaseModel):
    persona_id: int
    practice_topic_id: Optional[int] = None
    text_message: Optional[str] = None
    audio_message: Optional[str] = None

    @model_validator(mode="after")
    def check_one_message_type(self):
        if self.text_message is None and self.audio_message is None:
            raise ValueError("Either 'text_message' or 'audio_message' must be provided.")
        if self.text_message is not None and self.audio_message is not None:
            raise ValueError("Only one of 'text_message' or 'audio_message' can be provided.")
        return self
