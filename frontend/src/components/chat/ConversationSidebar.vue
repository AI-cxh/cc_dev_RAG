<template>
  <div
    class="bg-white border-r border-slate-200 flex flex-col transition-all duration-300"
    :class="showSidebar ? 'w-72' : 'w-0 overflow-hidden'"
  >
    <!-- Header -->
    <div class="p-4 border-b border-slate-200">
      <button
        @click="$emit('create')"
        class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition"
      >
        <PlusIcon class="w-4 h-4" />
        <span>新对话</span>
      </button>
    </div>

    <!-- Search -->
    <div class="p-2">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索对话..."
        class="w-full px-3 py-2 bg-slate-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
    </div>

    <!-- Conversation List -->
    <div class="flex-1 overflow-y-auto">
      <div
        v-for="conversation in filteredConversations"
        :key="conversation.id"
        class="group flex items-center gap-2 px-3 py-2 hover:bg-slate-50 cursor-pointer transition"
        :class="{ 'bg-slate-100': currentConversationId === conversation.id }"
        @click="$emit('select', conversation.id)"
      >
        <ChatBubbleLeftRightIcon class="w-4 h-4 text-slate-400" />
        <span class="flex-1 truncate text-sm text-slate-700">
          {{ conversation.title }}
        </span>
        <button
          @click.stop="$emit('delete', conversation.id)"
          class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition"
        >
          <TrashIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  PlusIcon,
  ChatBubbleLeftRightIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'
import type { Conversation } from '../../types'

interface Emits {
  (e: 'create'): void
  (e: 'select', id: number): void
  (e: 'delete', id: number): void
}

defineEmits<Emits>()

defineProps<{
  conversations: Conversation[]
  currentConversationId: number | null
  showSidebar?: boolean
}>()

const searchQuery = ref('')

const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) {
    return defineProps().conversations
  }
  const query = searchQuery.value.toLowerCase()
  return defineProps().conversations.filter((conv: Conversation) =>
    conv.title.toLowerCase().includes(query)
  )
})
</script>
