import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, streamChat } from '../api'
import type { Conversation, Message, Reference } from '../types'

export const useConversationStore = defineStore('conversations', () => {
  // State
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const currentConversationId = ref<number | null>(null)
  const streaming = ref(false)
  const streamingAnswer = ref('')
  const streamingReferences = ref<Reference[]>([])

  // Getters
  const sortedConversations = computed(() => {
    return [...conversations.value].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  })

  const currentMessages = computed(() => {
    return currentConversation.value?.messages || []
  })

  // Actions
  async function fetchConversations() {
    try {
      const data = await api.get('/v1/chat/conversations')
      conversations.value = data
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    }
  }

  async function fetchConversation(id: number) {
    try {
      const data = await api.get(`/v1/chat/conversations/${id}`)
      currentConversation.value = data
      currentConversationId.value = id
      return data
    } catch (error) {
      console.error('Failed to fetch conversation:', error)
    }
  }

  async function createConversation(title?: string) {
    try {
      const data = await api.post('/v1/chat/conversations', { title: title || 'New Conversation' })
      conversations.value.unshift(data)
      currentConversation.value = data
      currentConversationId.value = data.id
      return data
    } catch (error) {
      console.error('Failed to create conversation:', error)
    }
  }

  async function deleteConversation(id: number) {
    try {
      await api.delete(`/v1/chat/conversations/${id}`)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentConversationId.value === id) {
        currentConversation.value = null
        currentConversationId.value = null
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  async function* sendMessage(message: string, kbId: number | null = null) {
    streaming.value = true
    streamingAnswer.value = ''
    streamingReferences.value = []

    // Create conversation if none exists
    if (!currentConversationId.value) {
      const newConv = await createConversation()
      if (!newConv) {
        throw new Error('Failed to create conversation')
      }
    }

    try {
      for await (const chunk of streamChat(currentConversationId.value, message, kbId)) {
        // Handle different chunk types
        if (chunk.type === 'conversation_id') {
          currentConversationId.value = chunk.conversation_id
        } else if (chunk.type === 'content') {
          streamingAnswer.value += chunk.content || ''
          yield chunk
        } else if (chunk.type === 'references') {
          streamingReferences.value = chunk.references || []
          yield chunk
        } else if (chunk.type === 'done') {
          streaming.value = false
          yield chunk

          // Refresh conversation to get the complete message
          if (currentConversationId.value) {
            await fetchConversation(currentConversationId.value)
          }
        } else if (chunk.type === 'error') {
          streaming.value = false
          yield chunk
        }
      }
    } catch (error) {
      streaming.value = false
      throw error
    }
  }

  function clearStreaming() {
    streaming.value = false
    streamingAnswer.value = ''
    streamingReferences.value = []
  }

  function selectConversation(id: number) {
    const conv = conversations.value.find(c => c.id === id)
    if (conv) {
      currentConversation.value = conv
      currentConversationId.value = id
      fetchConversation(id)
    }
  }

  function createNewConversation() {
    currentConversation.value = null
    currentConversationId.value = null
  }

  return {
    // State
    conversations,
    currentConversation,
    currentConversationId,
    streaming,
    streamingAnswer,
    streamingReferences,

    // Getters
    sortedConversations,
    currentMessages,

    // Actions
    fetchConversations,
    fetchConversation,
    createConversation,
    deleteConversation,
    sendMessage,
    clearStreaming,
    selectConversation,
    createNewConversation,
  }
})
