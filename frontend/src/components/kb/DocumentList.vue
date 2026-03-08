<template>
  <div v-if="documents.length === 0" class="text-center py-8 text-slate-500">
    <DocumentIcon class="w-12 h-12 mx-auto mb-2 text-slate-300" />
    <p>还没有上传文档</p>
  </div>

  <div v-else class="space-y-2">
    <div
      v-for="doc in documents"
      :key="doc.id"
      class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition"
    >
      <!-- File type icon -->
      <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :class="getFileTypeClass(doc.file_type)">
        <component :is="getFileIcon(doc.file_type)" class="w-5 h-5" />
      </div>

      <!-- File info -->
      <div class="flex-1 min-w-0">
        <p class="font-medium text-slate-800 truncate">{{ doc.doc_name }}</p>
        <div class="flex items-center gap-3 text-sm text-slate-500">
          <span>{{ doc.file_type.toUpperCase() }}</span>
          <span>{{ formatSize(doc.file_size) }}</span>
          <span v-if="doc.metadata">{{ doc.metadata.total_chunks }} 个片段</span>
        </div>
      </div>

      <!-- Status -->
      <div class="flex items-center gap-2">
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="getStatusClass(doc.status)"
        >
          {{ getStatusText(doc.status) }}
        </span>

        <span
          v-if="doc.status === 'uploading' || doc.status === 'parsing' || doc.status === 'embedding'"
          class="text-xs text-slate-500"
        >
          {{ Math.round((doc.progress?.progress || 0) * 100) }}%
        </span>
      </div>

      <!-- Actions -->
      <button
        v-if="doc.status === 'completed'"
        @click="$emit('delete', doc.kb_id, doc.doc_id)"
        class="p-2 hover:bg-red-50 rounded-lg transition"
        title="删除"
      >
        <TrashIcon class="w-4 h-4 text-slate-400 hover:text-red-500" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  DocumentIcon,
  DocumentTextIcon,
  TrashIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline'
import type { Document } from '../../types'

interface Emits {
  (e: 'delete', kbId: number, docId: string): void
}

defineEmits<Emits>()

defineProps<{
  documents: Document[]
}>()

function getFileIcon(type: string) {
  const iconMap: Record<string, any> = {
    pdf: DocumentIcon,
    docx: DocumentTextIcon,
    md: DocumentTextIcon,
    txt: DocumentIcon,
  }
  return iconMap[type.toLowerCase()] || DocumentIcon
}

function getFileTypeClass(type: string) {
  const classMap: Record<string, string> = {
    pdf: 'bg-red-100 text-red-600',
    docx: 'bg-blue-100 text-blue-600',
    md: 'bg-purple-100 text-purple-600',
    txt: 'bg-slate-100 text-slate-600',
  }
  return classMap[type.toLowerCase()] || 'bg-slate-100 text-slate-600'
}

function getStatusClass(status: string) {
  const classMap: Record<string, string> = {
    uploading: 'bg-yellow-100 text-yellow-700',
    parsing: 'bg-blue-100 text-blue-700',
    chunking: 'bg-blue-100 text-blue-700',
    embedding: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  }
  return classMap[status] || 'bg-slate-100 text-slate-700'
}

function getStatusText(status: string) {
  const textMap: Record<string, string> = {
    uploading: '上传中',
    parsing: '解析中',
    chunking: '切分中',
    embedding: '向量化',
    completed: '已完成',
    failed: '失败',
  }
  return textMap[status] || status
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
