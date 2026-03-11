import os

from openai import OpenAI


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    return OpenAI(api_key=api_key)


def ai_match(resume_text: str, job_title: str, job_company: str) -> dict:
    """OpenAI API를 사용해 이력서-공고 간 적합도를 분석합니다."""
    client = get_client()

    prompt = f"""당신은 스포츠 테크 채용 전문가입니다.
아래 이력서와 채용공고를 비교 분석하여 JSON 형태로 응답하세요.

## 이력서
{resume_text[:3000]}

## 채용공고
- 회사: {job_company}
- 직무: {job_title}

## 응답 형식 (JSON만 출력)
{{
  "score": 0~100 정수 (적합도 점수),
  "summary": "한 줄 요약",
  "strengths": ["강점1", "강점2"],
  "suggestions": ["보완점1", "보완점2"]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return {
        "score": int(result.get("score", 0)),
        "summary": result.get("summary", ""),
        "strengths": result.get("strengths", []),
        "suggestions": result.get("suggestions", []),
    }
