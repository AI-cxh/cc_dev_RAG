<template>
  <div class="flex h-screen bg-slate-50">
    <!-- Sidebar -->
    <ConversationSidebar
      :conversations="sortedConversations"
      :current-conversation-id="currentConversationId"
      @select="selectConversation"
      @create="createNewConversation"
      @delete="deleteConversation"
    />

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <ChatHeader
        :current-kb="currentKnowledgeBase"
        @toggle-sidebar="showSidebar = !showSidebar"
        @open-kb-selector="showKBSelector = true"
      />

      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-4" ref="messagesContainer">
        <div v-if="!currentConversationId" class="flex items-center justify-center h-full text-slate-400">
          <div class="text-center">
            <p class="text-lg mb-2">开始新的对话</p>
            <p class="text-sm">选择知识库或直接开始聊天</p>
          </div>
        </div>

        <div v-else class="max-w-4xl mx-auto space-y-4">
          <ChatMessage
            v-for="message in currentMessages"
            :key="message.id"
            :message="message"
            @reference-click="handleReferenceClick"
          />

          <!-- Streaming message -->
          <ChatMessage
            v-if="streaming || streamingAnswer"
            :message="{
              role: 'assistant',
              content: streamingAnswer,
              metadata: { references: streamingReferences },
            }"
            :is-streaming="true"
            @reference-click="handleReferenceClick"
          />
        </div>
      </div>

      <!-- Input -->
      <ChatInput
        :disabled="streaming"
        @send="handleSendMessage"
      />
    </div>

    <!-- KB Selector Modal -->
    <KBSelectorModal
      :show="showKBSelector"
      :knowledge-bases="knowledgeBases"
      :current-kb-id="currentKnowledgeBase?.id"
      @close="showKBSelector = false"
      @select="handleSelectKB"
    />

    <!-- Reference Modal -->
    <ReferenceModal
      :show="referenceModal.show"
      :reference="referenceModal.reference"
      @close="referenceModal.show = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useConversationStore } from '../stores/conversations'
import { useKnowledgeBaseStore } from '../stores/knowledgeBase'
import ConversationSidebar from '../components/chat/ConversationSidebar.vue'
import ChatHeader from '../components/chat/ChatHeader.vue'
import ChatMessage from '../components/chat/ChatMessage.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import KBSelectorModal from '../components/chat/KBSelectorModal.vue'
import ReferenceModal from '../components/chat/ReferenceModal.vue'
import type { Reference } from '../types'

const conversationStore = useConversationStore()
const kbStore = useKnowledgeBaseStore()

const {
  conversations,
  currentConversationId,
  currentMessages,
  streaming,
  streamingAnswer,
  streamingReferences,
  sortedConversations,
  fetchConversations,
  selectConversation,
  createNewConversation,
  deleteConversation,
  sendMessage,
  clearStreaming,
} = conversationStore

const { knowledgeBases, currentKB, fetchKnowledgeBases, selectKB } = kbStore

const showSidebar = ref(true)
const showKBSelector = ref(false)
const messagesContainer = ref<HTMLElement>()
const currentKnowledgeBase = computed(() => currentKB.value)

// Reference Modal
const referenceModal = ref({
  show: false,
  reference: null as Reference | null,
})

async function handleSendMessage(message: string) {
  try {
    for await (const chunk of sendMessage(message, currentKB.value?.id || null)) {
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('发送消息失败，请重试')
  }
}

function handleReferenceClick(reference: Reference) {
  referenceModal.value.reference = reference
  referenceModal.value.show = true
}

function handleSelectKB(kbId: number | null) {
  if (kbId) {
    selectKB(kbId)
  } else {
    kbStore.clearSelection()
  }
  showKBSelector.value = false
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Auto-scroll when streaming
watch(streamingAnswer, () => {
  scrollToBottom()
})

onMounted(async () => {
  await Promise.all([
    fetchConversations(),
    fetchKnowledgeBases(),
  ])
})
</script>
