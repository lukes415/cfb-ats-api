from fastapi import APIRouter
from pydantic import BaseModel
from services.chat_service import chat_service
from services.cfbd_service import cfbd_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    year: int = 2024  # Default to current year

@router.post("")
async def chat(request: ChatRequest):
    """
    Ask questions about college football data
    Example: "How many times did Alabama cover in 2024?"
    """
    # Fetch relevant data (for now, just get all games for the year)
    games = await cfbd_service.fetch_games_for_year(request.year)
    
    # Get AI response
    result = await chat_service.answer_question(
        question=request.question,
        games_data=games
    )
    return result
    # return {
    #     "question": request.question,
    #     "answer": result["answer"],
    #     "year": request.year,
    #     "tokens_used": result["tokens_used"]
    # }