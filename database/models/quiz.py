from utils.firebase import db
from typing import List, Dict, Optional

class Quiz:
    def __init__(self, genres: List[str], mood: str, listening_preference: List[str], artists: List[str]):
        self.genres = genres
        self.mood = mood
        self.listening_preference = listening_preference
        self.artists = artists

    def to_dict(self) -> Dict:
        """Converts the Quiz object to a dictionary for Firestore."""
        return {
            "genres": self.genres,
            "mood": self.mood,
            "listening_preference": self.listening_preference,
            "artists": self.artists
        }


