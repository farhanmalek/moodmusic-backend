from fastapi import FastAPI
from routes import auth, quiz, playlists
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="MoodMusic API")

origins = [
    "http://localhost:3000",
    "http://localhost:3000/",
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
    return {"status": "healthy", "message": "MoodMusic API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


