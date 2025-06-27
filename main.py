from fastapi import FastAPI
from routes import auth, quiz, playlists
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="MoodMusic API")

# Get environment variables with defaults
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure CORS based on environment
origins = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3000/",
    "https://moodmusic-one.vercel.app/",
    "https://moodmusic-one.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(playlists.router, prefix="/playlists", tags=["playlists"])

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "MoodMusic API is running",
        "environment": ENVIRONMENT
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


