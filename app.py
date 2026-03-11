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
    "데이터",
    "AI",
    "머신러닝",
    "컴퓨터비전",
    "분석",
    "IoT",
    "웨어러블",
    "헬스케어",
    "플랫폼",
    "리그",
    "경기",
    "모션",
    "트래킹",
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


st.set_page_config(page_title="Sports Tech ATS", layout="wide")

st.title("Sports Tech ATS MVP")

resume_text = load_resume_texts()
jobs = load_jobs()

score = score_resume(resume_text, SPORTS_TECH_KEYWORDS)
matched_jobs = match_jobs(jobs, resume_text)

col1, col2, col3 = st.columns(3)
col1.metric("Resume Analysis Score", f"{score}%")
col2.metric("Jobs Collected", len(jobs))
col3.metric("Resume Keyword Matches", matched_jobs)

st.subheader("Live Job Postings")
if jobs:
    st.dataframe(jobs, use_container_width=True)
else:
    st.info("No jobs found. Run scraper.py to fetch postings.")
