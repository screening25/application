<template>
  <div>
    <div v-if="loading" class="loading">불러오는 중...</div>
    <template v-else>
      <!-- 통계 카드 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="label">이력서 분석 점수</div>
          <div class="value" :class="stats.resume_score >= 50 ? 'success' : 'warning'">
            {{ stats.resume_score }}%
          </div>
        </div>
        <div class="stat-card">
          <div class="label">수집된 공고</div>
          <div class="value">{{ stats.total_jobs }}</div>
        </div>
        <div class="stat-card">
          <div class="label">필터링 매칭</div>
          <div class="value success">{{ stats.filtered_jobs }}</div>
        </div>
      </div>

      <!-- 이력서 키워드 -->
      <div class="card">
        <h3>매칭 키워드</h3>
        <div class="keyword-tags" v-if="keywords.length">
          <span class="keyword-tag" v-for="kw in keywords" :key="kw">{{ kw }}</span>
        </div>
        <p v-else style="color: var(--text-muted); margin-top: 8px;">
          이력서를 업로드하면 매칭 키워드가 표시됩니다.
        </p>
      </div>

      <!-- AI 분석 -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3>AI 매칭 분석</h3>
          <button class="btn btn-primary" @click="runAI" :disabled="aiLoading">
            {{ aiLoading ? '분석 중...' : 'AI 분석 실행' }}
          </button>
        </div>
        <div v-if="aiResults.length" style="margin-top: 16px;">
          <div v-for="(item, i) in aiResults" :key="i" class="ai-result">
            <h4>{{ item.title }} — {{ item.company }}</h4>
            <template v-if="item.ai_analysis">
              <p><strong>적합도:</strong> {{ item.ai_analysis.score }}점 ・ {{ item.ai_analysis.summary }}</p>
              <p><strong>강점:</strong></p>
              <ul><li v-for="s in item.ai_analysis.strengths" :key="s">{{ s }}</li></ul>
              <p><strong>보완점:</strong></p>
              <ul><li v-for="s in item.ai_analysis.suggestions" :key="s">{{ s }}</li></ul>
            </template>
            <p v-else style="color: var(--text-muted);">AI 분석 불가 (API 키 미설정)</p>
          </div>
        </div>
        <p v-else style="color: var(--text-muted); margin-top: 12px;">
          이력서 업로드 후 AI 분석을 실행하면 상위 공고와의 적합도를 확인할 수 있습니다.
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { getDashboard, getResumeScore, aiAnalyze } from '../api'

const showToast = inject('showToast')

const loading = ref(true)
const aiLoading = ref(false)
const stats = ref({ resume_score: 0, total_jobs: 0, filtered_jobs: 0 })
const keywords = ref([])
const aiResults = ref([])

async function fetchData() {
  loading.value = true
  try {
    const [dashRes, scoreRes] = await Promise.all([getDashboard(), getResumeScore()])
    stats.value = dashRes.data
    keywords.value = scoreRes.data.matched_keywords
  } catch {
    showToast('데이터 로딩 실패', 'error')
  } finally {
    loading.value = false
  }
}

async function runAI() {
  aiLoading.value = true
  try {
    const res = await aiAnalyze()
    aiResults.value = res.data.analyzed_jobs
    showToast('AI 분석 완료')
  } catch (err) {
    const msg = err.response?.data?.detail || 'AI 분석 실패'
    showToast(msg, 'error')
  } finally {
    aiLoading.value = false
  }
}

onMounted(fetchData)
</script>
