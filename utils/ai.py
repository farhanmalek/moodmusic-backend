from dotenv import load_dotenv
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage




# Load API key
load_dotenv()
os.environ["OPEN_ROUTER_API"] = os.getenv("OPEN_ROUTER_API")

# Initialize OpenRouter LLM with DeepSeek R1
llm = ChatOpenAI(
    model_name="meta-llama/llama-3.3-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API"),
    temperature=0.1,
)

# User's quiz answers
user_preferences = {
    "preferred_genres": ["Hip-Hop", "R&B", "Pop"],
    "energy_level": "High",
    "release_decade": "2020s",
}

# Define the messages list with few-shot examples
messages = [
    SystemMessage(content="You are a music expert. Based on user preferences, suggest a playlist with about 15-20 songs, no more."),  
    HumanMessage(content=f"""
    The user wants a playlist from the movie "Sudent of the Year"
    User Preferences:
    - Favorite genres: Bollywood
    - Language: Hindi
    - Energy Level: Any
    
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
response = llm.invoke(messages)
print(response.content)

# Parse and print structured output
try:
    playlist_json = json.loads(response.content)  # Convert to dict
    print(json.dumps(playlist_json, indent=4))  # Pretty print JSON
except json.JSONDecodeError:
    print("Invalid JSON response:", response.content)
