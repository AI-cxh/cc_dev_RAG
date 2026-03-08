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
          class="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col"
          @click.stop
        >
          <!-- Header -->
          <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 class="text-lg font-semibold">引用详情</h2>
            <button @click="$emit('close')" class="p-1 hover:bg-slate-100 rounded-lg">
              <XMarkIcon class="w-5 h-5 text-slate-400" />
            </button>
          </div>

          <!-- Content -->
          <div v-if="reference" class="flex-1 overflow-y-auto p-6">
            <div class="space-y-4">
              <!-- Document Info -->
              <div>
                <p class="text-sm font-medium text-slate-500 mb-1">文档名称</p>
                <p class="text-lg font-semibold text-slate-800">
                  {{ reference.doc_name || '未知文档' }}
                </p>
              </div>

              <!-- URL if available -->
              <div v-if="reference.url">
                <p class="text-sm font-medium text-slate-500 mb-1">来源链接</p>
                <a
                  :href="reference.url"
                  target="_blank"
                  class="text-primary-600 hover:text-primary-700 flex items-center gap-1"
                >
                  <LinkIcon class="w-4 h-4" />
                  {{ reference.url }}
                </a>
              </div>

              <!-- Content -->
              <div>
                <p class="text-sm font-medium text-slate-500 mb-2">原文片段</p>
                <div class="bg-slate-50 rounded-lg p-4 text-slate-700 leading-relaxed">
                  {{ reference.content }}
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-slate-200 flex justify-end">
            <button
              @click="$emit('close')"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
            >
              关闭
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { XMarkIcon, LinkIcon } from '@heroicons/vue/24/outline'
import type { Reference } from '../../types'

interface Emits {
  (e: 'close'): void
}

defineEmits<Emits>()

defineProps<{
  show: boolean
  reference: Reference | null
}>()
</script>
