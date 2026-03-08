import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'
import type { LLMConfig, EmbeddingConfig, RerankerConfig } from '../types'

export const useSettingsStore = defineStore('settings', () => {
  // State
  const llmConfig = ref<LLMConfig>({
    vendor: 'openai',
    model: 'gpt-4o-mini',
    temperature: 0.7,
  })

  const embeddingConfig = ref<EmbeddingConfig>({
    vendor: 'openai',
    model: 'text-embedding-3-small',
    dimension: 1536,
  })

  const rerankerConfig = ref<RerankerConfig>({
    enabled: true,
    model: 'bge-reranker-v2-m3',
    top_k: 10,
  })

  const tavilyConfigured = ref(false)
  const loading = ref(false)

  // Actions
  async function fetchSettings() {
    loading.value = true
    try {
      const data = await api.get('/v1/config/settings')
      llmConfig.value = {
        vendor: data.llm.vendor,
        model: data.llm.model,
        temperature: 0.7,
      }
      embeddingConfig.value = {
        vendor: data.embedding.vendor,
        model: data.embedding.model,
        dimension: data.embedding.dimension,
      }
      rerankerConfig.value = {
        enabled: data.reranker_enabled,
        model: data.reranker_model,
        top_k: 10,
      }
      tavilyConfigured.value = data.tavily_configured
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      loading.value = false
    }
  }

  async function updateSettings() {
    loading.value = true
    try {
      const update = {
        llm: llmConfig.value,
        embedding: embeddingConfig.value,
        reranker: rerankerConfig.value,
      }
      // This would be implemented when the PUT endpoint exists
      console.log('Updating settings:', update)
    } catch (error) {
      console.error('Failed to update settings:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function updateLLMConfig(config: Partial<LLMConfig>) {
    llmConfig.value = { ...llmConfig.value, ...config }
  }

  function updateEmbeddingConfig(config: Partial<EmbeddingConfig>) {
    embeddingConfig.value = { ...embeddingConfig.value, ...config }
  }

  function updateRerankerConfig(config: Partial<RerankerConfig>) {
    rerankerConfig.value = { ...rerankerConfig.value, ...config }
  }

  return {
    // State
    llmConfig,
    embeddingConfig,
    rerankerConfig,
    tavilyConfigured,
    loading,

    // Actions
    fetchSettings,
    updateSettings,
    updateLLMConfig,
    updateEmbeddingConfig,
    updateRerankerConfig,
  }
})
