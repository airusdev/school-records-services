from fastapi import FastAPI, HTTPException
from decouple import config
import jwt
import asyncio
import asyncpg

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

