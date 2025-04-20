from utils.firebase import db
from typing import List, Dict, Optional
from .playlist import Playlist

class User:
    def __init__(self, id:str, username: str, quiz_answers: Optional[List] = None):
        self.id = id
        self.username = username
        self.quiz_answers = quiz_answers if quiz_answers is not None else dict()
        
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "quiz_answers": self.quiz_answers,
        }
        
    @staticmethod
    def from_dict(data: Dict) -> Optional["User"]:
        try:
            return User(
                id=data["id"],
                username=data["username"],
                quiz_answers=data.get("quiz_answers", {}),
            )
        except KeyError as e:
            print(f"Missing key in user data: {e}")
            return None
        
    def save(self) -> bool:
        try:
            doc_ref = db.collection("users").document(self.id).set(self.to_dict())
            return doc_ref is not None
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
                
    @staticmethod
    def get_by_id(user_id: str) -> Optional["User"]:
        try:
            doc = db.collection("users").document(user_id).get()
            if not doc.exists:
                return None
            return User.from_dict(doc.to_dict())
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None