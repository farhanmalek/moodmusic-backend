from fastapi import APIRouter, HTTPException
from utils.firebase import db
from database.models.quiz import Quiz
from pydantic import BaseModel

class QuizResponse(BaseModel):
    user_id: str
    genres: list[str]
    mood: str
    listening_preference: list[str]
    artists: list[str]


router = APIRouter()

@router.post("/")
def create_quiz(quiz: QuizResponse):
    # check if user exists
    user_id = quiz.user_id
    user_ref = db.collection("users").document(user_id)
    user = user_ref.get()
    if not user.exists:
        raise HTTPException(status_code=404, detail="User not found")
   
    if user.to_dict().get("quiz_answers"):
        raise HTTPException(status_code=400, detail="User already has a quiz")
    
    quiz_obj = Quiz(
        genres=quiz.genres,
        mood=quiz.mood,
        listening_preference=quiz.listening_preference,
        artists=quiz.artists
    )
    quiz_dict = quiz_obj.to_dict()
    user_ref.update({"quiz_answers": quiz_dict})
    return {"message": "Quiz created successfully"}