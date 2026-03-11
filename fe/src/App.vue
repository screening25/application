<template>
  <div class="app">
    <header class="app-header">
      <h1>⚽ Sports Tech ATS</h1>
      <nav class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="{ active: currentTab === tab.key }"
          @click="currentTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <DashboardView v-if="currentTab === 'dashboard'" />
    <JobList       v-if="currentTab === 'jobs'" />
    <ResumeUpload  v-if="currentTab === 'resume'" />

    <!-- 토스트 알림 -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import DashboardView from './components/DashboardView.vue'
import JobList from './components/JobList.vue'
import ResumeUpload from './components/ResumeUpload.vue'

const tabs = [
  { key: 'dashboard', label: '대시보드' },
  { key: 'jobs', label: '공고 목록' },
  { key: 'resume', label: '이력서' },
]

const currentTab = ref('dashboard')

const toast = ref({ show: false, message: '', type: 'success' })

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

provide('showToast', showToast)
</script>
