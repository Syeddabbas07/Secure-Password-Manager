from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import auth, generator, vault

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Password Manager",
    description="A FastAPI-based secure password manager project.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(generator.router)
app.include_router(vault.router)


@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "Secure Password Manager API is running",
        "version": "0.1.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {"status": "ok"}