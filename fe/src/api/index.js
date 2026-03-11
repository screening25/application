import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// ── 대시보드 ──
export function getDashboard() {
  return api.get('/dashboard')
}

// ── 공고 ──
export function getJobs() {
  return api.get('/jobs')
}

export function runScrape() {
  return api.post('/jobs/scrape')
}

// ── 이력서 ──
export function uploadResume(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/resume/upload', form)
}

export function getResumeScore() {
  return api.get('/resume/score')
}

// ── AI ──
export function aiAnalyze() {
  return api.post('/ai/analyze')
}

export function aiMatch(resumeText, jobTitle, jobCompany) {
  return api.post('/ai/match', {
    resume_text: resumeText,
    job_title: jobTitle,
    job_company: jobCompany,
  })
}
