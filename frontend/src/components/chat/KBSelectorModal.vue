<template>
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="$emit('close')"
    >
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4"
          @click.stop
        >
          <!-- Header -->
          <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 class="text-lg font-semibold">选择知识库</h2>
            <button @click="$emit('close')" class="p-1 hover:bg-slate-100 rounded-lg">
              <XMarkIcon class="w-5 h-5 text-slate-400" />
            </button>
          </div>

          <!-- Content -->
          <div class="p-6 space-y-2">
            <button
              @click="$emit('select', null)"
              class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition text-left"
              :class="{ 'bg-primary-50 border-2 border-primary-500': currentKbId === null }"
            >
              <div class="w-10 h-10 rounded-lg bg-slate-200 flex items-center justify-center">
                <XCircleIcon class="w-5 h-5 text-slate-500" />
              </div>
              <div class="flex-1">
                <p class="font-medium text-slate-800">不使用知识库</p>
                <p class="text-sm text-slate-500">仅使用联网搜索</p>
              </div>
            </button>

            <button
              v-for="kb in knowledgeBases"
              :key="kb.id"
              @click="$emit('select', kb.id)"
              class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition text-left"
              :class="{ 'bg-primary-50 border-2 border-primary-500': currentKbId === kb.id }"
            >
              <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                <BookOpenIcon class="w-5 h-5 text-primary-600" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-slate-800 truncate">{{ kb.name }}</p>
                <p class="text-sm text-slate-500">{{ kb.document_count }} 个文档</p>
              </div>
            </button>

            <p
              v-if="knowledgeBases.length === 0"
              class="text-center text-slate-500 py-4"
            >
              还没有创建知识库
            </p>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { XMarkIcon, XCircleIcon, BookOpenIcon } from '@heroicons/vue/24/outline'
import type { KnowledgeBase } from '../../types'

interface Emits {
  (e: 'close'): void
  (e: 'select', kbId: number | null): void
}

defineEmits<Emits>()

defineProps<{
  show: boolean
  knowledgeBases: KnowledgeBase[]
  currentKbId: number | null
}>()
</script>
