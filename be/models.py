from pydantic import BaseModel


class JobPosting(BaseModel):
    company: str
    title: str
    link: str
    deadline: str
    match_score: int = 0


class ResumeScore(BaseModel):
    score: int
    matched_keywords: list[str]


class AIMatchRequest(BaseModel):
    resume_text: str
    job_title: str
    job_company: str


class AIMatchResponse(BaseModel):
    score: int
    summary: str
    strengths: list[str]
    suggestions: list[str]


class DashboardStats(BaseModel):
    resume_score: int
    total_jobs: int
    filtered_jobs: int
