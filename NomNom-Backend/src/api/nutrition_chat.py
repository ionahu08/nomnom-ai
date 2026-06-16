import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.nutrition_chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse
from src.services.nutrition_chat_service import NutritionChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nutrition", tags=["nutrition"])


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatHistoryResponse:
    """Get chat message history for the current user."""
    try:
        logger.info(f"[NutritionChat] Loading chat history for user {current_user.id}")

        messages = await NutritionChatService.get_chat_history(db, current_user.id, limit=50)

        response_messages = [
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at,
            )
            for msg in messages
        ]

        logger.info(f"[NutritionChat] ✅ Loaded {len(response_messages)} messages for user {current_user.id}")

        return ChatHistoryResponse(messages=response_messages)

    except Exception as e:
        logger.error(f"[NutritionChat] Error loading chat history: {e}")
        logger.exception(f"[NutritionChat] Full traceback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load chat history: {str(e)}")


@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """
    Send a message to the nutrition coach and get a response.

    Returns the assistant's response message.
    """
    try:
        logger.info(f"[NutritionChat] Received message from user {current_user.id}: {request.message[:50]}...")

        # Save user message
        user_msg = await NutritionChatService.save_message(
            db, current_user.id, "user", request.message
        )
        logger.info(f"[NutritionChat] Saved user message: {user_msg.id}")

        # Get response from Claude
        response_text = await NutritionChatService.get_chat_response(
            db, current_user, request.message
        )

        if response_text is None:
            logger.warning(f"[NutritionChat] Failed to generate response for user {current_user.id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate coach response"
            )

        # Save assistant response
        assistant_msg = await NutritionChatService.save_message(
            db, current_user.id, "assistant", response_text
        )
        logger.info(f"[NutritionChat] ✅ Saved assistant response: {assistant_msg.id}")

        return ChatMessageResponse(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            timestamp=assistant_msg.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[NutritionChat] Error processing chat message: {e}")
        logger.exception(f"[NutritionChat] Full traceback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")
