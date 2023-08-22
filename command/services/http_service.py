import uvicorn
from fastapi import FastAPI

from threading import Thread

app = FastAPI()

@app.get("/")
async def home() -> dict:

    return {"hello": "world"}
