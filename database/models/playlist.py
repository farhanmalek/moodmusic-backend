from utils.firebase import db
from typing import  Dict, Optional
from datetime import datetime

class Playlist:
    def __init__(self, id:str,  name: str, query: str, image: Optional[str] = None, timecreated: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.query = query
        self.timecreated = timecreated or datetime.now()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "query": self.query,
            "timecreated": self.timecreated.isoformat(),
        }
        
    @staticmethod
    def from_dict(data: Dict) -> 'Playlist':
        return Playlist(
            id=data["id"],
            name=data["name"],
            query=data["query"],
            timecreated=datetime.fromisoformat(data["timecreated"]),
        )


