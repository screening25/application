<template>
  <div>
    <h2 style="margin-bottom: 16px;">이력서 관리</h2>

    <!-- 업로드 -->
    <div class="card">
      <h3>PDF 업로드</h3>
      <div class="upload-zone" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onDrop">
        <p style="font-size: 2rem;">📄</p>
        <p>클릭하거나 PDF 파일을 드래그하세요</p>
      </div>
      <input ref="fileInput" type="file" accept=".pdf" hidden @change="onFileSelect" />

      <div v-if="uploadedFile" style="margin-top: 12px; display: flex; align-items: center; gap: 12px;">
        <span>{{ uploadedFile }}</span>
        <button class="btn btn-success" @click="upload" :disabled="uploading">
          {{ uploading ? '업로드 중...' : '업로드' }}
        </button>
      </div>
    </div>

    <!-- 이력서 분석 결과 -->
    <div class="card">
      <h3>이력서 분석</h3>
      <div v-if="scoreLoading" class="loading">분석 중...</div>
      <template v-else-if="score !== null">
        <div class="stats-grid" style="margin-top: 12px;">
          <div class="stat-card">
            <div class="label">키워드 매칭 점수</div>
            <div class="value" :class="score >= 50 ? 'success' : 'warning'">{{ score }}%</div>
          </div>
        </div>
        <div class="keyword-tags" v-if="matchedKeywords.length">
          <span class="keyword-tag" v-for="kw in matchedKeywords" :key="kw">{{ kw }}</span>
        </div>
      </template>
      <p v-else style="color: var(--text-muted); margin-top: 8px;">
        이력서를 업로드하면 분석 결과가 표시됩니다.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { uploadResume, getResumeScore } from '../api'

const showToast = inject('showToast')

const fileInput = ref(null)
const selectedFile = ref(null)
const uploadedFile = ref('')
const uploading = ref(false)
const score = ref(null)
const matchedKeywords = ref([])
const scoreLoading = ref(false)

function onFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    uploadedFile.value = file.name
  }
}

function onDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.name.toLowerCase().endsWith('.pdf')) {
    selectedFile.value = file
    uploadedFile.value = file.name
  }
}

async function upload() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    await uploadResume(selectedFile.value)
    showToast('이력서 업로드 완료')
    selectedFile.value = null
    uploadedFile.value = ''
    await fetchScore()
  } catch {
    showToast('업로드 실패', 'error')
  } finally {
    uploading.value = false
  }
}

async function fetchScore() {
  scoreLoading.value = true
  try {
    const res = await getResumeScore()
    score.value = res.data.score
    matchedKeywords.value = res.data.matched_keywords
  } catch {
    score.value = null
  } finally {
    scoreLoading.value = false
  }
}

onMounted(fetchScore)
</script>
