from __future__ import annotations

import dataclasses

from fastapi import APIRouter, File, UploadFile, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.resume_pipeline import analyze_uploaded_resume
from app.services.resume_ranker import rank_candidates, CandidateScore
from app.db.session import get_db
from app.db.models import Resume, Analysis, User, UserRole
from app.core.deps import require_role
from app.core.logging_config import logger

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

templates = Jinja2Templates(directory="app/templates")

MAX_FILES = 100
CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.get("")
async def recruiter_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="recruiter.html",
    )


@router.post(
    "/upload",
    summary="Upload multiple resumes",
    description="Upload multiple PDF/DOCX resumes, rank candidates, and persist results.",
)
async def upload_resumes(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES} resumes allowed.",
        )

    candidates = []
    errors = []

    valid_fields = {f.name for f in dataclasses.fields(CandidateScore)}

    for file in files:
        try:
            chunks = []
            total_size = 0

            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > 10 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail=f"{file.filename} exceeds the 10 MB limit.",
                    )

                chunks.append(chunk)

            file_bytes = b"".join(chunks)

            result_dict = analyze_uploaded_resume(
                filename=file.filename or "",
                file_bytes=file_bytes,
            )

            filtered = {k: v for k, v in result_dict.items() if k in valid_fields}
            result = CandidateScore(**filtered)
            candidates.append(result)

        except HTTPException as e:
            errors.append(
                {
                    "filename": file.filename,
                    "error": e.detail,
                }
            )
        except Exception as e:
            logger.exception("An error occurred")
            raise

    ranked = rank_candidates(candidates)

    # --- Persist every successful analysis ---
    for candidate in ranked:
        resume_row = Resume(filename=candidate.filename)
        db.add(resume_row)
        await db.flush()  # populates resume_row.id before we reference it below

        analysis_row = Analysis(
            resume_id=resume_row.id,
            ats_score=candidate.ats_score,
            job_match=candidate.job_match,
            semantic_match=candidate.semantic_match,
            project_score=candidate.project_score,
            overall_score=candidate.overall_score,
            rank=candidate.rank,
            recommendation=candidate.recommendation,
            matching_skills=candidate.matching_skills,
            missing_skills=candidate.missing_skills,
        )
        db.add(analysis_row)

    await db.commit()
    # --- End persistence ---

    return {
        "total_candidates": len(candidates),
        "failed": len(errors),
        "errors": errors,
        "candidates": ranked,
    }


@router.get(
    "/history",
    summary="View past resume analyses",
    description="Returns every previously analyzed resume, most recent first.",
)
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    stmt = (
        select(Analysis, Resume)
        .join(Resume, Analysis.resume_id == Resume.id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    history = []
    for analysis_row, resume_row in rows:
        history.append(
            {
                "filename": resume_row.filename,
                "uploaded_at": resume_row.uploaded_at.isoformat(),
                "ats_score": analysis_row.ats_score,
                "job_match": analysis_row.job_match,
                "semantic_match": analysis_row.semantic_match,
                "project_score": analysis_row.project_score,
                "overall_score": analysis_row.overall_score,
                "rank": analysis_row.rank,
                "recommendation": analysis_row.recommendation,
                "matching_skills": analysis_row.matching_skills,
                "missing_skills": analysis_row.missing_skills,
            }
        )

    return {"total": len(history), "history": history}