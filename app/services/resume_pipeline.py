"""
Resume Processing Pipeline

This service provides one reusable pipeline for processing uploaded
resumes. It validates the file, extracts text, runs the analyzer,
and returns the final analysis.

Both upload.py and recruiter.py should use this service.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.services.parser import (
    SUPPORTED_EXTENSIONS,
    UnsupportedFileType,
    extract_text,
    get_extension,
)

from app.utils.constants import MAX_FILE_SIZE_BYTES
from app.utils.helper import analyze_resume


def analyze_uploaded_resume(
    *,
    filename: str,
    file_bytes: bytes,
    candidate_name: str | None = None,
    role: str | None = None,
    job_description: str | None = None,
) -> dict:
    """
    Complete resume processing pipeline.

    Steps
    -----
    1. Validate file extension
    2. Validate size
    3. Extract resume text
    4. Analyze resume
    5. Return frontend-ready JSON
    """

    extension = get_extension(filename)

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension or 'unknown'}'. Upload a PDF or DOCX resume.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB upload limit.",
        )

    try:
        text = extract_text(filename, file_bytes)

    except UnsupportedFileType as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Unable to read this resume. "
                "The file may be scanned, corrupted, or password protected."
            ),
        ) from exc

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the uploaded resume.",
        )

    result = analyze_resume(
        text=text,
        job_description=job_description,
    )

    return {
        "message": "Resume analyzed successfully.",
        "filename": filename,
        "candidate_name": candidate_name,
        "role": role,
        **result.to_dict(),
    }