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
          <!-- Icon -->
          <div class="p-6 text-center">
            <div class="w-16 h-16 mx-auto rounded-full bg-red-100 flex items-center justify-center mb-4">
              <ExclamationTriangleIcon class="w-8 h-8 text-red-600" />
            </div>
            <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ title }}</h3>
            <p class="text-slate-600">{{ message }}</p>
          </div>

          <!-- Footer -->
          <div class="px-6 pb-6 flex justify-center gap-3">
            <button
              @click="$emit('close')"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
            >
              取消
            </button>
            <button
              @click="$emit('confirm')"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
            >
              确认
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'close'): void
  (e: 'confirm'): void
}

defineEmits<Emits>()

defineProps<{
  show: boolean
  title: string
  message: string
}>()
</script>
