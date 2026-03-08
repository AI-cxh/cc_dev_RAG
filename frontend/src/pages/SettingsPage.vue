<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <div class="bg-white border-b border-slate-200 px-6 py-4">
      <div class="max-w-4xl mx-auto flex items-center gap-4">
        <router-link
          to="/"
          class="p-2 hover:bg-slate-100 rounded-lg transition"
        >
          <ArrowLeftIcon class="w-6 h-6 text-slate-600" />
        </router-link>
        <h1 class="text-xl font-semibold text-slate-800">系统设置</h1>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto p-6">
      <div class="space-y-6">
        <!-- LLM Settings -->
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-200 flex items-center gap-3">
            <CpuChipIcon class="w-5 h-5 text-primary-600" />
            <h2 class="font-semibold text-slate-800">LLM 模型配置</h2>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">模型供应商</label>
              <div class="grid grid-cols-3 gap-3">
                <button
                  v-for="vendor in llmVendors"
                  :key="vendor.value"
                  @click="llmConfig.vendor = vendor.value as any"
                  class="p-3 border-2 rounded-lg text-center transition"
                  :class="llmConfig.vendor === vendor.value ? 'border-primary-500 bg-primary-50' : 'border-slate-200 hover:border-slate-300'"
                >
                  <p class="font-medium">{{ vendor.name }}</p>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">模型名称</label>
              <select
                v-model="llmConfig.model"
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option v-for="model in availableLLMModels" :key="model.id" :value="model.id">
                  {{ model.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">API Key</label>
              <input
                v-model="apiKey"
                type="password"
                placeholder="sk-..."
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        <!-- Embedding Settings -->
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-200 flex items-center gap-3">
            <BeakerIcon class="w-5 h-5 text-primary-600" />
            <h2 class="font-semibold text-slate-800">Embedding 模型配置</h2>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">模型</label>
              <select
                v-model="embeddingConfig.model"
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option v-for="model in availableEmbeddingModels" :key="model.id" :value="model.id">
                  {{ model.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="font-semibold text-slate-800 mb-4">服务状态</h2>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-slate-600">Tavily 搜索</span>
              <span
                class="px-3 py-1 rounded-full text-sm"
                :class="tavilyConfigured ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
              >
                {{ tavilyConfigured ? '已配置' : '未配置' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <button
          @click="handleSave"
          :disabled="saving"
          class="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white rounded-xl transition font-medium"
        >
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ArrowLeftIcon, CpuChipIcon, BeakerIcon } from '@heroicons/vue/24/outline'
import { useSettingsStore } from '../stores/settings'
import { api } from '../api'

const settingsStore = useSettingsStore()

const { llmConfig, embeddingConfig, tavilyConfigured, loading, fetchSettings } = settingsStore

const saving = ref(false)
const apiKey = ref('')

const llmVendors = [
  { name: 'OpenAI', value: 'openai' },
  { name: 'VLLM', value: 'vllm' },
  { name: 'Ollama', value: 'ollama' },
]

const availableLLMModels = [
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'llama3', name: 'Llama 3 (Ollama)' },
  { id: 'mistral', name: 'Mistral (Ollama)' },
]

const availableEmbeddingModels = [
  { id: 'text-embedding-3-small', name: 'Text Embedding 3 Small' },
  { id: 'text-embedding-3-large', name: 'Text Embedding 3 Large' },
  { id: 'bge-m3', name: 'BGE-M3' },
]

async function handleSave() {
  saving.value = true
  try {
    // Update settings
    await settingsStore.updateSettings()
    alert('设置已保存')
  } catch (error) {
    alert('保存设置失败，请重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
