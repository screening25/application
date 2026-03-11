<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h2>공고 목록</h2>
      <button class="btn btn-primary" @click="scrape" :disabled="scraping">
        {{ scraping ? '수집 중...' : '공고 새로고침' }}
      </button>
    </div>

    <div v-if="loading" class="loading">불러오는 중...</div>

    <div v-else-if="!jobs.length" class="empty-state">
      <p>수집된 공고가 없습니다.</p>
      <p>위 버튼을 눌러 공고를 수집해 보세요.</p>
    </div>

    <div v-else class="card" style="overflow-x: auto;">
      <table class="job-table">
        <thead>
          <tr>
            <th>매칭</th>
            <th>회사</th>
            <th>직무</th>
            <th>마감</th>
            <th>AI</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(job, i) in jobs" :key="i">
            <td>
              <span :class="['score-badge', scoreCls(job.match_score)]">
                {{ job.match_score }}
              </span>
            </td>
            <td>{{ job.company }}</td>
            <td>
              <a :href="job.link" target="_blank" rel="noopener noreferrer">{{ job.title }}</a>
            </td>
            <td>{{ job.deadline }}</td>
            <td>
              <button class="btn btn-primary" style="padding: 4px 12px; font-size: 0.8rem;"
                      @click="analyzeJob(job)" :disabled="job._aiLoading">
                {{ job._aiLoading ? '...' : '분석' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- AI 분석 모달 -->
    <div v-if="selectedAI" class="card" style="margin-top: 16px;">
      <div style="display: flex; justify-content: space-between;">
        <h3>AI 분석 결과</h3>
        <button @click="selectedAI = null" style="cursor: pointer; background: none; border: none; font-size: 1.2rem;">&times;</button>
      </div>
      <div class="ai-result" style="margin-top: 8px;">
        <p><strong>적합도:</strong> {{ selectedAI.score }}점</p>
        <p>{{ selectedAI.summary }}</p>
        <p><strong>강점:</strong></p>
        <ul><li v-for="s in selectedAI.strengths" :key="s">{{ s }}</li></ul>
        <p><strong>보완점:</strong></p>
        <ul><li v-for="s in selectedAI.suggestions" :key="s">{{ s }}</li></ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { getJobs, runScrape, aiMatch, getResumeScore } from '../api'

const showToast = inject('showToast')

const loading = ref(true)
const scraping = ref(false)
const jobs = ref([])
const selectedAI = ref(null)
const resumeText = ref('')

function scoreCls(score) {
  if (score >= 40) return 'score-high'
  if (score >= 20) return 'score-mid'
  return 'score-low'
}

async function fetchJobs() {
  loading.value = true
  try {
    const res = await getJobs()
    jobs.value = res.data.map(j => ({ ...j, _aiLoading: false }))
  } catch {
    showToast('공고 로딩 실패', 'error')
  } finally {
    loading.value = false
  }
}

async function scrape() {
  scraping.value = true
  try {
    const res = await runScrape()
    showToast(`${res.data.collected}개 공고 수집 완료`)
    await fetchJobs()
  } catch {
    showToast('스크래핑 실패', 'error')
  } finally {
    scraping.value = false
  }
}

async function analyzeJob(job) {
  if (!resumeText.value) {
    showToast('이력서를 먼저 업로드해 주세요.', 'error')
    return
  }
  job._aiLoading = true
  try {
    const res = await aiMatch(resumeText.value, job.title, job.company)
    selectedAI.value = res.data
  } catch (err) {
    const msg = err.response?.data?.detail || 'AI 분석 실패'
    showToast(msg, 'error')
  } finally {
    job._aiLoading = false
  }
}

onMounted(async () => {
  await fetchJobs()
  try {
    const scoreRes = await getResumeScore()
    // store for AI calls
    resumeText.value = scoreRes.data.matched_keywords.join(' ')
  } catch { /* 이력서 없음 */ }
})
</script>
