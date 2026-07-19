from dotenv import load_dotenv
load_dotenv()

import time   

from app.core.logging_config import logger
from app.api.system import router as system_router

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.upload import router as upload_router
from app.api.recruiter import router as recruiter_router
from app.api.auth import router as auth_router

app = FastAPI(title="AI Resume Screener")



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start

    logger.info(
        f"{request.method} {request.url.path} | "
        f"Status={response.status_code} | "
        f"Time={duration:.3f}s"
    )

    return response



import platform

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

app.include_router(upload_router, prefix="/api")
app.include_router(recruiter_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(system_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    logger.info("Application started")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )