SPORTS_TECH_KEYWORDS = [
    "스포츠", "체육", "운동", "퍼포먼스", "경기", "리그", "선수", "팀",
    "트레이닝", "컨디션", "부상", "웨어러블", "센서", "IoT", "GPS",
    "EPTS", "트래킹", "모니터링", "분석", "데이터",
]

EXCLUDE_KEYWORDS = [
    "강사", "레슨", "코치", "트레이너", "PT", "판매",
    "영업", "매장", "서비스직", "아르바이트", "시설관리",
]


def score_resume(resume_text: str) -> tuple[int, list[str]]:
    """이력서 텍스트를 키워드 매칭하여 점수와 매칭 키워드 목록 반환."""
    if not resume_text:
        return 0, []

    lowered = resume_text.lower()
    matched = [kw for kw in SPORTS_TECH_KEYWORDS if kw.lower() in lowered]
    score = min(100, int(len(matched) / len(SPORTS_TECH_KEYWORDS) * 100))
    return score, matched


def score_job(job: dict) -> int:
    """단일 공고에 대한 매칭 점수 계산. 0이면 필터링 대상."""
    title = job.get("title", "")
    company = job.get("company", "")
    combined = f"{title} {company}".lower()

    if any(kw.lower() in combined for kw in EXCLUDE_KEYWORDS):
        return 0

    matched = sum(1 for kw in SPORTS_TECH_KEYWORDS if kw.lower() in combined)
    if matched == 0:
        return 0

    return min(100, matched * 10)
