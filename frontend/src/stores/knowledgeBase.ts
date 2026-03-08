import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'
import type { KnowledgeBase, Document } from '../types'

export const useKnowledgeBaseStore = defineStore('knowledgeBase', () => {
  // State
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const currentKB = ref<KnowledgeBase | null>(null)
  const documents = ref<Document[]>([])
  const uploading = ref(false)

  // Getters
  const totalDocuments = computed(() => {
    return knowledgeBases.value.reduce((sum, kb) => sum + kb.document_count, 0)
  })

  const currentKBDocuments = computed(() => {
    return documents.value.filter(doc => doc.kb_id === currentKB.value?.id)
  })

  // Actions
  async function fetchKnowledgeBases() {
    try {
      const data = await api.get('/v1/kbs')
      knowledgeBases.value = data
    } catch (error) {
      console.error('Failed to fetch knowledge bases:', error)
    }
  }

  async function createKnowledgeBase(name: string, description: string = '') {
    try {
      const data = await api.post('/v1/kbs', { name, description })
      knowledgeBases.value.push(data)
      await fetchKnowledgeBases()
      return data
    } catch (error) {
      console.error('Failed to create knowledge base:', error)
      throw error
    }
  }

  async function deleteKnowledgeBase(id: number) {
    try {
      await api.delete(`/v1/kbs/${id}`)
      knowledgeBases.value = knowledgeBases.value.filter(kb => kb.id !== id)
      if (currentKB.value?.id === id) {
        currentKB.value = null
        documents.value = []
      }
    } catch (error) {
      console.error('Failed to delete knowledge base:', error)
      throw error
    }
  }

  async function selectKB(id: number) {
    const kb = knowledgeBases.value.find(k => k.id === id)
    if (kb) {
      currentKB.value = kb
      await fetchDocuments(id)
    }
  }

  function clearSelection() {
    currentKB.value = null
    documents.value = []
  }

  async function fetchDocuments(kbId: number) {
    try {
      const data = await api.get(`/v1/kbs/${kbId}/documents`)
      documents.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
  }

  async function uploadDocument(kbId: number, file: File) {
    uploading.value = true

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post(`/v1/kbs/${kbId}/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Start polling for progress
      await pollDocumentProgress(kbId, response.document_id)

      return response
    } catch (error) {
      console.error('Failed to upload document:', error)
      throw error
    } finally {
      uploading.value = false
    }
  }

  async function pollDocumentProgress(kbId: number, docId: number) {
    const maxAttempts = 120 // 2 minutes
    let attempts = 0

    const interval = setInterval(async () => {
      attempts++

      try {
        await fetchDocuments(kbId)
        const doc = documents.value.find(d => d.id === docId)

        if (!doc || doc.status === 'completed' || doc.status === 'failed' || attempts >= maxAttempts) {
          clearInterval(interval)
          if (currentKB.value) {
            currentKB.value = { ...currentKB.value, document_count: documents.value.length }
          }
          await fetchKnowledgeBases()
        }
      } catch (error) {
        console.error('Error polling document progress:', error)
        clearInterval(interval)
      }
    }, 1000)
  }

  async function deleteDocument(kbId: number, docId: string) {
    try {
      await api.delete(`/v1/kbs/${kbId}/documents/${docId}`)
      documents.value = documents.value.filter(doc => doc.doc_id !== docId)
      if (currentKB.value) {
        currentKB.value = { ...currentKB.value, document_count: documents.value.length }
      }
      await fetchKnowledgeBases()
    } catch (error) {
      console.error('Failed to delete document:', error)
      throw error
    }
  }

  return {
    // State
    knowledgeBases,
    currentKB,
    documents,
    uploading,

    // Getters
    totalDocuments,
    currentKBDocuments,

    // Actions
    fetchKnowledgeBases,
    createKnowledgeBase,
    deleteKnowledgeBase,
    selectKB,
    clearSelection,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
  }
})
