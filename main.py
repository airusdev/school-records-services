from contextlib import asynccontextmanager
from decouple import config
import asyncpg
from fastapi import FastAPI, Depends, Request, HTTPException

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASSWORD")
DB_NAME = config("DB_NAME")
DB_PORT = config("DB_PORT", cast=int)
DB_HOST = config("DB_HOST")

DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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

@app.get("/students")
async def list_students(conn: asyncpg.Connection = Depends(get_connection)):
    rows = await conn.fetch(
        'SELECT * FROM students'
    )
    return rows

@app.get("/students/{stud_id}")
async def get_student(stud_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    row = await conn.fetchrow(
        'SELECT * FROM students WHERE student_id = $1',
        stud_id
    )

    if not row:
        raise HTTPException(status_code=404, detail=f"Student ID: {stud_id} does not exist.")

    return [dict(row)]
