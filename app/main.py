from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers import auth, generator, vault


Base.metadata.create_all(bind=engine)

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
FRONTEND_DIRECTORY = BASE_DIRECTORY / "frontend"
STATIC_DIRECTORY = FRONTEND_DIRECTORY / "static"


app = FastAPI(
    title="Secure Password Manager",
    description=(
        "A secure FastAPI password manager using "
        "JWT authentication and AES-GCM encryption."
    ),
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIRECTORY),
    name="static",
)

app.include_router(auth.router)
app.include_router(generator.router)
app.include_router(vault.router)


@app.get(
    "/",
    include_in_schema=False,
)
def frontend_home():
    return FileResponse(
        FRONTEND_DIRECTORY / "index.html"
    )


@app.get(
    "/dashboard",
    include_in_schema=False,
)
def frontend_dashboard():
    return FileResponse(
        FRONTEND_DIRECTORY / "dashboard.html"
    )


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "ok",
        "service": "secure-password-manager",
    }