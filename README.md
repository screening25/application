# Sports Tech ATS

스포츠-IT 융합 직무 특화 ATS (Applicant Tracking System)

## 프로젝트 구조

```
be/          ← FastAPI 백엔드
  main.py        API 서버 엔트리포인트
  scraper.py     사람인 스크래퍼
  models.py      Pydantic 스키마
  services/
    scoring.py   키워드 매칭 스코어링
    ai_match.py  OpenAI API 연동

fe/          ← Vue 3 프론트엔드
  src/
    App.vue            메인 레이아웃
    api/index.js       API 클라이언트
    components/
      DashboardView.vue  대시보드
      JobList.vue        공고 목록
      ResumeUpload.vue   이력서 관리
```

## 빠른 시작

### 1. 백엔드 실행
```bash
cd be
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt

# (선택) AI 매칭 기능 사용 시
# be/.env 파일에 OPENAI_API_KEY 설정

uvicorn main:app --reload
```
API 문서: http://localhost:8000/docs

### 2. 프론트엔드 실행
```bash
cd fe
npm install
npm run dev
```
UI: http://localhost:5173

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/dashboard` | 대시보드 통계 |
| GET | `/api/jobs` | 필터링된 공고 목록 |
| POST | `/api/jobs/scrape` | 스크래퍼 실행 |
| POST | `/api/resume/upload` | 이력서 PDF 업로드 |
| GET | `/api/resume/score` | 이력서 매칭 점수 |
| POST | `/api/ai/match` | AI 이력서-공고 매칭 |
| POST | `/api/ai/analyze` | 상위 공고 AI 일괄 분석 |