<template>
  <div class="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-2 hover:bg-slate-100 rounded-lg transition"
      >
        <Bars3Icon class="w-6 h-6 text-slate-600" />
      </button>
      <h1 class="text-xl font-semibold text-slate-800">对话</h1>
    </div>

    <div class="flex items-center gap-4">
      <!-- KB Selector -->
      <button
        @click="$emit('open-kb-selector')"
        class="flex items-center gap-2 px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
      >
        <BookOpenIcon class="w-5 h-5 text-slate-600" />
        <span class="text-sm text-slate-700">
          {{ currentKb ? currentKb.name : '未选择知识库' }}
        </span>
        <ChevronDownIcon class="w-4 h-4 text-slate-400" />
      </button>

      <!-- Settings link -->
      <router-link
        to="/settings"
        class="p-2 hover:bg-slate-100 rounded-lg transition"
        title="设置"
      >
        <Cog6ToothIcon class="w-6 h-6 text-slate-600" />
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bars3Icon, BookOpenIcon, ChevronDownIcon, Cog6ToothIcon } from '@heroicons/vue/24/outline'
import type { KnowledgeBase } from '../../types'

interface Emits {
  (e: 'toggle-sidebar'): void
  (e: 'open-kb-selector'): void
}

defineEmits<Emits>()

defineProps<{
  currentKb: KnowledgeBase | null
}>()
</script>
