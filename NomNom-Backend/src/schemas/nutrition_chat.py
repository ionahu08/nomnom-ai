from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
