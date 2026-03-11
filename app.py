import json
from pathlib import Path

import streamlit as st
from PyPDF2 import PdfReader


RESUME_DIR = Path("resumes")
JOBS_PATH = Path("data/jobs.json")
SPORTS_TECH_KEYWORDS = [
    "스포츠",
    "체육",
    "운동",
    "퍼포먼스",
    "경기",
    "리그",
    "선수",
    "팀",
    "트레이닝",
    "컨디션",
    "부상",
    "웨어러블",
    "센서",
    "IoT",
    "GPS",
    "EPTS",
    "트래킹",
    "모니터링",
    "분석",
    "데이터",
]

EXCLUDE_KEYWORDS = [
    "강사",
    "레슨",
    "코치",
    "트레이너",
    "PT",
    "판매",
    "영업",
    "매장",
    "서비스직",
    "아르바이트",
    "시설관리",
]


def load_resume_texts() -> str:
    texts = []
    if not RESUME_DIR.exists():
        return ""

    for pdf_path in RESUME_DIR.glob("*.pdf"):
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            texts.append(page.extract_text() or "")

    return "\n".join(texts).strip()


def load_jobs() -> list[dict]:
    if not JOBS_PATH.exists():
        return []

    with JOBS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def score_resume(resume_text: str, keywords: list[str]) -> int:
    if not resume_text:
        return 0

    matched = sum(1 for keyword in keywords if keyword.lower() in resume_text.lower())
    if not keywords:
        return 0

    return min(100, int(matched / len(keywords) * 100))


def match_jobs(jobs: list[dict], resume_text: str) -> int:
    if not resume_text:
        return 0

    lowered = resume_text.lower()
    count = 0
    for job in jobs:
        title = job.get("title", "").lower()
        if any(keyword.lower() in lowered for keyword in title.split()):
            count += 1

    return count


def score_job(job: dict) -> int:
    title = job.get("title", "")
    company = job.get("company", "")
    combined = f"{title} {company}".lower()
    if any(keyword.lower() in combined for keyword in EXCLUDE_KEYWORDS):
        return 0

    matched = sum(1 for keyword in SPORTS_TECH_KEYWORDS if keyword.lower() in combined)
    if matched == 0:
        return 0

    return min(100, matched * 10)


st.set_page_config(page_title="Sports Tech ATS", layout="wide")

st.title("Sports Tech ATS MVP")

resume_text = load_resume_texts()
jobs = load_jobs()
scored_jobs = []
for job in jobs:
    score = score_job(job)
    if score == 0:
        continue
    job_with_score = dict(job)
    job_with_score["match_score"] = score
    scored_jobs.append(job_with_score)

score = score_resume(resume_text, SPORTS_TECH_KEYWORDS)
matched_jobs = match_jobs(jobs, resume_text)

col1, col2, col3 = st.columns(3)
col1.metric("Resume Analysis Score", f"{score}%")
col2.metric("Jobs Collected", len(jobs))
col3.metric("Filtered Matches", len(scored_jobs))

st.subheader("Live Job Postings")
if scored_jobs:
    st.dataframe(scored_jobs, use_container_width=True)
else:
    st.info("No matching jobs found. Try re-running scraper.py or refining keywords.")
