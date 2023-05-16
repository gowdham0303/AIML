from fastapi import FastAPI
from route import audio


app = FastAPI()
app.include_router(audio.router)

