from fastapi import FastAPI
from routes import auth, quiz, playlists

app = FastAPI()

# Routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(playlists.router, prefix="/playlists", tags=["playlists"])

@app.get("/")
def read_root():
    return {"Hello": "World"}


