from utils.firebase import db
from typing import List, Dict, Optional

class Quiz:
    def __init__(self, language: str, time_period: str, listening_preference: List[str], artists: List[str]):
        self.language = language
        self.time_period = time_period
        self.listening_preference = listening_preference
        self.artists = artists

    def to_dict(self) -> Dict:
        """Converts the Quiz object to a dictionary for Firestore."""
        return {
            "language": self.language,
            "time_period": self.time_period,
            "listening_preference": self.listening_preference,
            "artists": self.artists
        }


