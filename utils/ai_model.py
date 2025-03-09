from dotenv import load_dotenv
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class AIModel:
    def __init__(self, quiz_answers, prompt: str):
        self.quiz_answers = quiz_answers
        self.prompt = prompt

        # Load API key
        load_dotenv()
        self.api_key = os.getenv("OPEN_ROUTER_API")

        if not self.api_key:
            raise ValueError("OPEN_ROUTER_API key is missing. Check your .env file.")

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            model_name="meta-llama/llama-3.3-70b-instruct:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            temperature=0,
        )

    def get_playlist(self):
        # Ensure quiz_answers has the required attributes
        try:
            genres = ', '.join(self.quiz_answers["genres"]) if self.quiz_answers["genres"] else "Unknown"
            artists = ', '.join(self.quiz_answers["artists"]) if self.quiz_answers["artists"] else "Unknown"
            listening_pref = ', '.join(self.quiz_answers["listening_preference"]) if self.quiz_answers["listening_preference"] else "Unknown"
            
        except AttributeError as e:
            raise ValueError(f"Invalid quiz_answers object: {e}")

        messages = [
            SystemMessage(content="You are a music expert. Based on the given prompt, suggest a playlist with about 15-20 songs, no more."),
            HumanMessage(content=f"""
            {self.prompt}
            
            Do not make up any songs or artists. Use real songs and artists only.
        
            Return a valid JSON response ONLY, strictly in this format:
            {{
                "playlist": [
                    {{"title": "Song 1", "artist": "Artist 1"}},
                    {{"title": "Song 2", "artist": "Artist 2"}}
                ],
                description: "A generic description of the playlist noting key songs, artists and genres and why the songs were chosen."
            }}
            No extra text before or after the JSON response.
            """),
        ]

        # Send query
        response = self.llm.invoke(messages)

        # Parse response
        try:
            playlist_json = json.loads(response.content) if response.content else {"playlist": []}
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response from AI.")
            playlist_json = {"playlist": []}

        return playlist_json
