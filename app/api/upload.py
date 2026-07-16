from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.resume_pipeline import analyze_uploaded_resume
from app.utils.constants import MAX_FILE_SIZE_BYTES

router = APIRouter(prefix="/upload", tags=["upload"])

CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str | None = Form(None),
    role: str | None = Form(None),
    job_description: str | None = Form(None),
):
    chunks: list[bytes] = []
    total_size = 0

    while True:
        chunk = await file.read(CHUNK_SIZE)

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File is larger than the 10MB limit.",
            )

        chunks.append(chunk)

    file_bytes = b"".join(chunks)

    return analyze_uploaded_resume(
        filename=file.filename or "",
        file_bytes=file_bytes,
        candidate_name=candidate_name,
        role=role,
        job_description=job_description,
    )