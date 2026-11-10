# fix the representation of returned information from database

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from decouple import config # for .env
import asyncpg
from tabulate import tabulate

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "This is the school db REST API!"} 


@app.get("/students", response_class=HTMLResponse)
async def list_students():
    conn = await asyncpg.connect(
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        database=config("DB_NAME"),
        host=config("DB_HOST")
    )
    values = await conn.fetch(
        'SELECT * FROM students'
    )

    await conn.close()
    
    text_table = tabulate(values, headers="keys")
    return f"<pre>{text_table}</pre>"


@app.get("/students/{id}", response_class=HTMLResponse)
async def get_student(student_id: int):
    conn = await asyncpg.connect(
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        database=config("DB_NAME"),
        host=config("DB_HOST")
    )
    values = await conn.fetch(
        f"SELECT * FROM students WHERE student_id = {student_id}"
    )
    
    await conn.close()
    text_table = tabulate(values, headers="keys")
    
    if text_table != '':
        return f"<pre>{text_table}</pre"
    
    return "[ERROR] Student not found!"


@app.get("/courses", response_class=HTMLResponse)
async def list_courses():
    conn = await asyncpg.connect(
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        database=config("DB_NAME"),
        host=config("DB_HOST")
    )
    values = await conn.fetch(
        'SELECT * FROM courses'
    )
    
    await conn.close()
    
    text_table = tabulate(values, headers="keys")
    return f"<pre>{text_table}</pre>"


@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def get_course(course_id: int):
    conn = await asyncpg.connect(
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        database=config("DB_NAME"),
        host=config("DB_HOST")
    )
    values = await conn.fetch(
        f"SELECT * FROM courses WHERE course_id = {course_id}"
    )
    
    await conn.close()
    text_table = tabulate(values, headers="keys")

    if text_table != "":
        return f"<pre>{text_table}</pre>"
    
    return "[ERROR] Course not found!"
