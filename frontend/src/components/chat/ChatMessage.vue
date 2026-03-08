<template>
  <div
    class="flex"
    :class="isUser ? 'justify-end' : 'justify-start'"
  >
    <div
      class="flex-1 max-w-[80%]"
    >
      <div
        class="rounded-2xl p-4"
        :class="messageClass"
      >
        <!-- Message content -->
        <div class="markdown-content" v-html="renderedContent"></div>

        <!-- References -->
        <div
          v-if="references && references.length > 0"
          class="mt-4 pt-4 border-t border-white/20"
        >
          <p class="text-xs font-medium mb-2 opacity-75">引用来源:</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="(ref, index) in references"
              :key="index"
              @click="$emit('reference-click', ref)"
              class="reference-chip"
            >
              [{{ ref.id }}] {{ ref.doc_name || '来源 ' + (ref.id + 1) }}
            </button>
          </div>
        </div>

        <!-- Streaming indicator -->
        <div v-if="isStreaming" class="flex items-center gap-1 mt-2">
          <span class="w-2 h-2 bg-current rounded-full pulse-ring"></span>
          <span class="w-2 h-2 bg-current rounded-full pulse-ring" style="animation-delay: 0.2s"></span>
          <span class="w-2 h-2 bg-current rounded-full pulse-ring" style="animation-delay: 0.4s"></span>
        </div>
      </div>

      <!-- Timestamp -->
      <p class="text-xs text-slate-400 mt-1" :class="isUser ? 'text-right' : 'text-left'">
        {{ formattedTime }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import type { Message, Reference } from '../../types'

interface Props {
  message: Message | { role: string; content: string; metadata?: { references?: Reference[] } }
  isStreaming?: boolean
}

const props = defineProps<Props>()

interface Emits {
  (e: 'reference-click', reference: Reference): void
}

defineEmits<Emits>()

configureMarked()

function configureMarked() {
  marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
      // Basic code highlighting - can be enhanced with highlight.js
      return code
    },
  })
}

const isUser = computed(() => props.message.role === 'user')

const messageClass = computed(() => {
  return isUser.value
    ? 'chat-message-user'
    : 'chat-message-assistant'
})

const renderedContent = computed(() => {
  const html = marked(props.message.content)
  return DOMPurify.sanitize(html)
})

const references = computed(() => {
  return props.message.metadata?.references || []
})

const formattedTime = computed(() => {
  if (!('created_at' in props.message)) return ''
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})
</script>
