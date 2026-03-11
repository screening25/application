import json
from pathlib import Path

from fastmcp import FastMCP
from PyPDF2 import PdfReader


mcp = FastMCP("sports-tech-ats")


@mcp.tool()
def read_resume_pdf(filename: str) -> str:
    """Read a resume PDF from ./resumes and return extracted text."""
    resume_path = Path("resumes") / filename
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    reader = PdfReader(str(resume_path))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")

    return "\n".join(pages_text).strip()


@mcp.resource("jobs://latest")
def get_latest_jobs() -> dict:
    """Return the latest scraped jobs from data/jobs.json."""
    jobs_path = Path("data/jobs.json")
    if not jobs_path.exists():
        return {"jobs": []}

    with jobs_path.open("r", encoding="utf-8") as handle:
        jobs = json.load(handle)

    return {"jobs": jobs}


if __name__ == "__main__":
    mcp.run()
