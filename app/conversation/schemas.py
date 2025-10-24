from typing import Optional

from pydantic import BaseModel, Field

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
