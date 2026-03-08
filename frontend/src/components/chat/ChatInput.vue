<template>
  <div class="bg-white border-t border-slate-200 p-4">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-end gap-3">
        <textarea
          v-model="message"
          :disabled="disabled"
          placeholder="输入消息... (Shift+Enter 换行, Enter 发送)"
          class="flex-1 resize-none border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400"
          rows="1"
          :style="{ maxHeight: '200px' }"
          @keydown.enter.exact.prevent="handleSend"
          @keydown.shift.enter.exact="handleNewline"
          @input="autoResize"
          ref="textareaRef"
        />

        <button
          @click="handleSend"
          :disabled="disabled || !message.trim()"
          class="px-4 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl transition flex items-center gap-2"
        >
          <PaperAirplaneIcon class="w-5 h-5" />
          <span v-if="!isMobile">发送</span>
        </button>
      </div>

      <p class="text-xs text-slate-400 mt-2 text-center">
        按 <kbd class="px-1 py-0.5 bg-slate-100 rounded">Enter</kbd> 发送，
        <kbd class="px-1 py-0.5 bg-slate-100 rounded">Shift + Enter</kbd> 换行
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { PaperAirplaneIcon } from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'send', message: string): void
}

defineEmits<Emits>()

defineProps<{
  disabled?: boolean
}>()

const message = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

const isMobile = computed(() => window.innerWidth < 768)

function handleSend() {
  const trimmed = message.value.trim()
  if (trimmed && !defineProps().disabled) {
    defineEmits().send?.(trimmed)
    message.value = ''

    // Reset height
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
}

function handleNewline() {
  // Let the default behavior work
  emit('keydown.shift.enter.exact')
}

function autoResize(e: Event) {
  const target = e.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = Math.min(target.scrollHeight, 200) + 'px'
}

// Initial cursor position
setTimeout(() => {
  textareaRef.value?.focus()
}, 100)
</script>
