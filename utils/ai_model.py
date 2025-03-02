from dotenv import load_dotenv
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ..database.models.quiz import Quiz


class AIModel:
    def __init__(self, quiz_answers: Quiz, prompt: str):
        self.quiz_answers = quiz_answers
        self.prompt = prompt
        
        # Load API key
        load_dotenv()
        os.environ["OPEN_ROUTER_API"] = os.getenv("OPEN_ROUTER_API")
        
        self.llm = ChatOpenAI(
            model_name="meta-llama/llama-3.3-70b-instruct:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API"),
            temperature=0.1,
        )
        
    def get_playlist(self):
        messages = [
            SystemMessage(content="You are a music expert. Based on user preferences, suggest a playlist with about 15-20 songs, no more."),
            HumanMessage(content=f"""
            {self.prompt}
            
            User Preferences:
            - Favorite genres: {', '.join(self.quiz_answers.genres)}
            - Favorite artists: {', '.join(self.quiz_answers.artists)}
            - Listening preferences: {', '.join(self.quiz_answers.listening_preference)}
            
            Take into consideration these preferences above but do not include them if they are not applicable to the prompt.
            
            Return a valid JSON response ONLY, strictly in this format:
            {{
                "playlist": [
                    {{"title": "Song 1", "artist": "Artist 1"}},
                    {{"title": "Song 2", "artist": "Artist 2"}}
                ]
            }}
            No extra text before or after the JSON response.
            """),
        ]

        # Send query
        response = self.llm.invoke(messages)

        if response.content != "":
            playlist_json = json.loads(response.content)
        else:
            playlist_json = {"playlist": []}
               
            
        return playlist_json
