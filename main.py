from contextlib import asynccontextmanager
from decouple import config
import asyncpg
from fastapi import FastAPI, status, Depends, Request, HTTPException
from pydantic import BaseModel, StrictInt, field_validator
import re

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASSWORD")
DB_NAME = config("DB_NAME")
DB_PORT = config("DB_PORT", cast=int)
DB_HOST = config("DB_HOST")

DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# request body validatiaon
# class Student(BaseModel):
#     student_id: StrictInt
#     student_name: str

#     @field_validator("student_name")
#     def validate_name(cls, value):
#         if not re.match(r"^[a-zA-Z\s]+$", value):
#             raise ValueError("Name can only contain letters and spaces.")
#         return value.strip()

class AcquireStudentName(BaseModel):
    student_name: str

    @field_validator("student_name")
    def validate_name(cls, value):
        if not re.match(r"^[a-zA-Z\s]+$", value):
            raise ValueError("Name can only contain letters and spaces.")
        if len(value) <= 1:
            raise ValueError("Name must be longer than 2 letters.")
        return value.strip()

# set up a connection pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        dsn=DB_URL,
        min_size = 5,
        max_size = 20,
        max_inactive_connection_lifetime=300.0,
        command_timeout=30.0
    )
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

async def get_connection(request: Request):
    pool = request.app.state.pool
    async with pool.acquire(timeout=5.0) as conn:
        yield conn


# students
@app.get("/students")
async def list_students(conn: asyncpg.Connection = Depends(get_connection)):
    rows = await conn.fetch(
        'SELECT * FROM students'
    )

    if not rows:
        raise HTTPException(status_code=404, details=f"Table: 'students' does not exist.")
    elif rows == []:
        raise HTTPException(status_code=204, details=f"Table exists however data does not exist yet.")

    return rows

@app.get("/students/{stud_id}")
async def get_student(stud_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    if stud_id <= 0:
        raise HTTPException(status_code=400, detail=f"Student ID: {stud_id} must be greater than or equal to 1")

    row = await conn.fetchrow(
        'SELECT * FROM students WHERE student_id = $1',
        stud_id
    )

    if not row:
        raise HTTPException(status_code=404, detail=f"Student ID: {stud_id} does not exist")

    return row

@app.post("/students", status_code=status.HTTP_201_CREATED)
async def input_student(stud: AcquireStudentName, conn: asyncpg.Connection = Depends(get_connection)):
    await conn.fetchrow(
        """INSERT INTO students (student_name)
        VALUES ($1)""",
        stud.student_name
    )

    return {"message": "Student added!", "student": stud}

@app.delete("/students/{stud_id}")
async def delete_student(stud_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    if stud_id <= 0:
        raise HTTPException(status_code=400, detail=f"Student ID must be greater than 0.")

    exists = await conn.fetchval(
        'SELECT COUNT(*) FROM students WHERE student_id = $1',
        stud_id
    )

    if exists == 0:
        raise HTTPException(status_code=404, detail=f"Student ID: {stud_id} have already been removed or does not exist")
   
    await conn.fetchrow(
        'DELETE FROM students WHERE student_id = $1',
        stud_id
    )

    return {"message": "Deleted student!", "Student ID": stud_id}
