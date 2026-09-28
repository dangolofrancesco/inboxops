from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.applications import router as applications_router
from app.api.auth import router as auth_router
from app.api.gmail import router as gmail_router

app = FastAPI(
    title="InboxOps API",
    description="Personal operations layer built on email",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)

app.include_router(auth_router)

app.include_router(gmail_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "inboxops-api", "version": "0.1.0"}

    