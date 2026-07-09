from fastapi import FastAPI

from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Password Manager",
    description="A FastAPI-based secure password manager project.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Secure Password Manager API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}