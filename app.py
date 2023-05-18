from fastapi import FastAPI
from route import audio, questions
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(audio.router)
app.include_router(questions.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set the allowed origins here (e.g., ["http://localhost", "https://example.com"])
    allow_credentials=True,
    allow_methods=["*"],  # Set the allowed HTTP methods here (e.g., ["GET", "POST"])
    allow_headers=["*"],  # Set the allowed headers here (e.g., ["Content-Type"])
)
