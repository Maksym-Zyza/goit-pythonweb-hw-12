from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from src.database.models import Base
from src.database.db import engine
from src.database.db import get_db
from src.routers import contacts, auth, users

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def create_tables():
    Base.metadata.create_all(engine)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


@app.get("/", name="API root")
def get_index():
    return {"message": "Welcome to root API"}


@app.get("/health", name="Server availability")
def get_health(db=Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1+1")).fetchone()
        print(">>", result)
        if result is None:
            raise Exception

        return {"message": "API is up and ready for the requests"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DB is not configured correctly",
        )


@app.get("/me", name="Route with rate limiting")
@limiter.limit("5/minute")
async def my_endpoint(request: Request):
    return {"message": "This is my route with rate limiting."}


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
