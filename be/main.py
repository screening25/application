import json
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from models import JobPosting, ResumeScore, AIMatchRequest, AIMatchResponse, DashboardStats
from scraper import fetch_jobs
from services.scoring import score_resume, score_job
from services.ai_match import ai_match

app = FastAPI(title="Sports Tech ATS API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
RESUME_DIR = Path("resumes")


# ── 유틸 ────────────────────────────────────────────────
def _load_jobs() -> list[dict]:
    jobs_path = DATA_DIR / "jobs.json"
    if not jobs_path.exists():
        return []
    with jobs_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_resume_text() -> str:
    texts = []
    if not RESUME_DIR.exists():
        return ""
    for pdf in RESUME_DIR.glob("*.pdf"):
        reader = PdfReader(str(pdf))
        for page in reader.pages:
            texts.append(page.extract_text() or "")
    return "\n".join(texts).strip()


# ── 공고 API ────────────────────────────────────────────
@app.get("/api/jobs", response_model=list[JobPosting])
def get_jobs():
    """필터링된 공고 목록 반환."""
    raw = _load_jobs()
    result = []
    for job in raw:
        s = score_job(job)
        if s > 0:
            result.append({**job, "match_score": s})
    result.sort(key=lambda x: x["match_score"], reverse=True)
    return result


@app.post("/api/jobs/scrape")
def run_scrape():
    """스크래퍼를 실행하고 수집된 공고 수를 반환."""
    jobs = fetch_jobs(out_path=str(DATA_DIR / "jobs.json"))
    return {"collected": len(jobs)}


# ── 이력서 API ──────────────────────────────────────────
@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """이력서 PDF 업로드."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    dest = RESUME_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"filename": file.filename, "message": "업로드 완료"}


@app.get("/api/resume/score", response_model=ResumeScore)
def get_resume_score():
    """현재 이력서의 키워드 매칭 점수."""
    text = _read_resume_text()
    score, matched = score_resume(text)
    return ResumeScore(score=score, matched_keywords=matched)


# ── 대시보드 API ────────────────────────────────────────
@app.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard():
    """대시보드 통계."""
    text = _read_resume_text()
    r_score, _ = score_resume(text)
    raw = _load_jobs()
    filtered = [j for j in raw if score_job(j) > 0]
    return DashboardStats(
        resume_score=r_score,
        total_jobs=len(raw),
        filtered_jobs=len(filtered),
    )


# ── AI 매칭 API ─────────────────────────────────────────
@app.post("/api/ai/match", response_model=AIMatchResponse)
def ai_match_endpoint(req: AIMatchRequest):
    """OpenAI API를 사용한 이력서-공고 AI 매칭 분석."""
    result = ai_match(req.resume_text, req.job_title, req.job_company)
    return AIMatchResponse(**result)


@app.post("/api/ai/analyze")
def ai_analyze_resume():
    """저장된 이력서를 기반으로 상위 공고들과 AI 매칭 분석."""
    text = _read_resume_text()
    if not text:
        raise HTTPException(status_code=404, detail="이력서가 없습니다. 먼저 업로드해 주세요.")

    raw = _load_jobs()
    scored = []
    for job in raw:
        s = score_job(job)
        if s > 0:
            scored.append({**job, "match_score": s})
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # 상위 5개만 AI 분석
    results = []
    for job in scored[:5]:
        try:
            analysis = ai_match(text, job["title"], job["company"])
            results.append({**job, "ai_analysis": analysis})
        except RuntimeError:
            results.append({**job, "ai_analysis": None})
            break

    return {"analyzed_jobs": results}
