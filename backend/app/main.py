from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InboxOps API",
    description="Personal operations layer built on email",
    version="0.1.0",
)

# Starlette builds the middleware stack lazily on the first request, wrapping
# whatever is registered at that point. Adding CORSMiddleware here, before any
# routes/routers are included, guarantees it wraps every endpoint (including
# ones added later) rather than depending on registration order elsewhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "inboxops-api", "version": "0.1.0"}
