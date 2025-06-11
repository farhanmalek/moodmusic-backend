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
            temperature=0.7,
        )

    def get_playlist(self):
        # Ensure quiz_answers has the required attributes
        try:
            language = ', '.join(self.quiz_answers["language"]) if self.quiz_answers.get("language") else "Any"
            time_period = self.quiz_answers.get("time_period", "Any")
            listening_pref = ', '.join(self.quiz_answers["listening_preference"]) if self.quiz_answers.get("listening_preference") else "Any"
            artists = ', '.join(self.quiz_answers["artists"]) if self.quiz_answers.get("artists") else "Any"
            
        except AttributeError as e:
            raise ValueError(f"Invalid quiz_answers object: {e}")
    
        # Prepare messages
        messages = [
        SystemMessage(content="You are a highly knowledgeable music expert with deep familiarity with global music trends across different genres and time periods."),
        HumanMessage(content=f"""
        Generate a playlist with 30 songs, based on the following user preferences and prompt.

        **User Preferences (Persistent)**
        - Preferred Language: {language}
        - Preferred Time Period: {time_period}
        - General Listening Preference: {listening_pref}
        - Favorite Artists: {artists}
        

        **User Prompt for Playlist Generation**
        {self.prompt}

        **Requirements for the Response**
        - Do NOT make up any songs or artists. Only use real, existing music.
        - Ensure the playlist reflects the user’s preferences while staying relevant to the provided prompt.
        - If a song features multiple artists, only list the main artist and the most relevant collaborator.
        - Return ONLY valid JSON in this format:     
        {{
            "playlist": [
                {{"title": "Song 1", "artist": "Artist 1"}},
                {{"title": "Song 2", "artist": "Artist 2"}}
            ],
        }}
           
        - The response must be **pure JSON** with no additional text or explanations.
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
