from fastapi import FastAPI, HTTPException
from decouple import config

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


