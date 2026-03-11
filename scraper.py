import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.saramin.co.kr/zf_user/search"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


@dataclass
class JobPosting:
    company: str
    title: str
    link: str
    deadline: str


def _contains_noise(text: str, noise_keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in noise_keywords)


def fetch_jobs(
    keyword: str = "스포츠 테크",
    max_pages: int = 1,
    out_path: str = "data/jobs.json",
    noise_keywords: Iterable[str] | None = None,
    sleep_seconds: float = 1.0,
) -> list[JobPosting]:
    if noise_keywords is None:
        noise_keywords = [
            "단순 서비스",
            "단순서비스",
            "판매",
            "영업",
            "매장",
            "서비스직",
            "카운터",
            "레슨",
            "시설관리",
            "관리",
        ]

    collected: list[JobPosting] = []

    for page in range(1, max_pages + 1):
        params = {
            "searchword": keyword,
            "recruitPage": page,
            "recruitPageCount": 40,
        }
        response = requests.get(BASE_URL, params=params, headers=DEFAULT_HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select("div.item_recruit"):
            title_tag = item.select_one("h2.job_tit a") or item.select_one("a.str_tit")
            company_tag = (
                item.select_one("div.area_corp strong.corp_name a")
                or item.select_one("a.str_tit")
            )
            deadline_tag = item.select_one("span.date")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True) if company_tag else ""
            link = title_tag.get("href", "")
            if link.startswith("/"):
                link = f"https://www.saramin.co.kr{link}"
            deadline = deadline_tag.get_text(strip=True) if deadline_tag else ""

            combined = f"{title} {company}"
            if _contains_noise(combined, noise_keywords):
                continue

            collected.append(JobPosting(company=company, title=title, link=link, deadline=deadline))

        time.sleep(sleep_seconds)

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as handle:
        json.dump([job.__dict__ for job in collected], handle, ensure_ascii=False, indent=2)

    return collected


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"Collected {len(jobs)} jobs")
