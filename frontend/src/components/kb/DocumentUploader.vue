<template>
  <div
    class="border-2 border-dashed rounded-xl p-6 text-center transition-colors"
    :class="isDragging ? 'border-primary-500 bg-primary-50' : 'border-slate-300 hover:border-primary-400 hover:bg-slate-50'"
    @dragover.prevent="isDragging = true"
    @dragleave="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".pdf,.docx,.md,.txt"
      multiple
      class="hidden"
      @change="handleFileSelect"
    />

    <div class="space-y-2">
      <CloudArrowUpIcon class="w-12 h-12 text-slate-400 mx-auto" />
      <p class="text-slate-700">
        <button
          @click="fileInput?.click()"
          class="text-primary-600 hover:text-primary-700 font-medium"
        >
          点击上传
        </button>
        或将文件拖到此处
      </p>
      <p class="text-sm text-slate-500">
        支持 PDF、DOCX、MD、TXT 格式，单个知识库最多 10 个文档
      </p>
    </div>

    <!-- File list -->
    <div v-if="files.length > 0" class="mt-4 space-y-2">
      <div
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center justify-between p-3 bg-white rounded-lg border"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <DocumentIcon class="w-5 h-5 text-slate-400 flex-shrink-0" />
          <span class="truncate text-sm">{{ file.name }}</span>
          <span class="text-xs text-slate-400">{{ formatSize(file.size) }}</span>
        </div>
        <button
          @click="removeFile(index)"
          class="p-1 hover:bg-slate-100 rounded transition"
        >
          <XMarkIcon class="w-4 h-4 text-slate-400" />
        </button>
      </div>

      <button
        @click="uploadFiles"
        :disabled="uploading"
        class="w-full py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white rounded-lg transition"
      >
        {{ uploading ? '上传中...' : '开始上传' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/vue/24/outline'

interface Emits {
  (e: 'upload', kbId: number, file: File): void
}

defineEmits<Emits>()

defineProps<{
  kbId: number
  uploading?: boolean
}>()

const isDragging = ref(false)
const files = ref<File[]>([])
const fileInput = ref<HTMLInputElement>()

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const dropped = e.dataTransfer?.files
  if (dropped) {
    addFiles(Array.from(dropped))
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
    target.value = '' // Reset
  }
}

function addFiles(newFiles: File[]) {
  const allowedExtensions = ['.pdf', '.docx', '.md', '.txt']
  const validFiles = newFiles.filter(file => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    return allowedExtensions.includes(ext)
  })

  files.value.push(...validFiles)
}

function removeFile(index: number) {
  files.value.splice(index, 1)
}

async function uploadFiles() {
  for (const file of files.value) {
    defineEmits().upload?.(defineProps().kbId, file)
  }
  files.value = []
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
