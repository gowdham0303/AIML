from fastapi import FastAPI
from route import audio, questions


app = FastAPI()
app.include_router(audio.router)
app.include_router(questions.router)
