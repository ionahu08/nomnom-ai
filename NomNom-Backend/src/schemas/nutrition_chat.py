from pydantic import BaseModel, Field, field_serializer
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        """Ensure timestamp is ISO8601 formatted with Z suffix for UTC."""
        if value.tzinfo is None:
            return value.isoformat() + "Z"
        return value.isoformat()


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
