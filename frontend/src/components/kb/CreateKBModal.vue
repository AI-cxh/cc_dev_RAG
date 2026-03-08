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
          <div class="px-6 py-4 border-b border-slate-200">
            <h2 class="text-lg font-semibold">创建知识库</h2>
          </div>

          <!-- Form -->
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">
                知识库名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="name"
                type="text"
                placeholder="例如：技术文档、产品手册..."
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                maxlength="100"
              />
              <p class="text-xs text-slate-500 mt-1">{{ name.length }}/100</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">
                描述
              </label>
              <textarea
                v-model="description"
                placeholder="简要描述这个知识库的内容..."
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                rows="3"
                maxlength="500"
              />
              <p class="text-xs text-slate-500 mt-1">{{ description.length }}/500</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
            <button
              @click="$emit('close')"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
            >
              取消
            </button>
            <button
              @click="handleCreate"
              :disabled="!name.trim()"
              class="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-lg transition"
            >
              创建
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Emits {
  (e: 'close'): void
  (e: 'create', name: string, description: string): void
}

defineEmits<Emits>()

defineProps<{
  show: boolean
}>()

const name = ref('')
const description = ref('')

function handleCreate() {
  if (name.value.trim()) {
    defineEmits().create?.(name.value.trim(), description.value.trim())
    name.value = ''
    description.value = ''
  }
}
</script>
