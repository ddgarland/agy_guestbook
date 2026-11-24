import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models import (
    init_db,
    add_entry,
    get_entries,
    GuestbookEntry
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    init_db()
    yield

app = FastAPI(
    title="Cloud Run Guestbook",
    description="A guestbook application running on Google Cloud Run",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "script-src 'self';"
    )
    return response

@app.get("/health", tags=["Operational"])
@app.get("/api/healthz", tags=["Operational"])
@app.get("/healthz", tags=["Operational"])
async def health_check():
    """Healthcheck probe endpoint for container readiness and liveness."""
    return {"status": "healthy", "service": "guestbook-app"}

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def render_guestbook(request: Request, success: bool = False):
    entries = get_entries(limit=50)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "entries": entries,
            "success": success,
            "error": None,
            "form_data": None
        }
    )

@app.post("/entries", tags=["UI"])
async def submit_entry(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        # Validate input with Pydantic model
        validated = GuestbookEntry(
            name=name.strip(),
            email=email.strip(),
            message=message.strip()
        )
        add_entry(
            name=validated.name,
            email=str(validated.email),
            message=validated.message
        )
        # Post/Redirect/Get pattern
        return RedirectResponse(url="/?success=true", status_code=status.HTTP_303_SEE_OTHER)
    except ValidationError as ve:
        error_msg = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in ve.errors()])
        entries = get_entries(limit=50)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "entries": entries,
                "success": False,
                "error": f"Validation Error: {error_msg}",
                "form_data": {"name": name, "email": email, "message": message}
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

@app.get("/api/v1/entries", response_model=List[dict], tags=["API"])
async def list_entries():
    """API endpoint to query guestbook entries as JSON."""
    return get_entries(limit=50)
