<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <div class="bg-white border-b border-slate-200 px-6 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link
            to="/"
            class="p-2 hover:bg-slate-100 rounded-lg transition"
          >
            <ArrowLeftIcon class="w-6 h-6 text-slate-600" />
          </router-link>
          <h1 class="text-xl font-semibold text-slate-800">知识库管理</h1>
        </div>
        <button
          @click="showCreateModal = true"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
        >
          <PlusIcon class="w-5 h-5" />
          <span>创建知识库</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto p-6">
      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl p-6 border border-slate-200">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-primary-100 flex items-center justify-center">
              <BookOpenIcon class="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-slate-800">{{ knowledgeBases.length }}</p>
              <p class="text-sm text-slate-500">知识库总数</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-6 border border-slate-200">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <DocumentIcon class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-slate-800">{{ totalDocuments }}</p>
              <p class="text-sm text-slate-500">文档总数</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl p-6 border border-slate-200">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-amber-100 flex items-center justify-center">
              <BookOpenIcon class="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p class="text-2xl font-bold text-slate-800">{{ currentKB?.name || '-' }}</p>
              <p class="text-sm text-slate-500">当前选中的知识库</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Knowledge Bases List -->
      <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">知识库列表</h2>
          <p class="text-sm text-slate-500">最多每个知识库 10 个文档</p>
        </div>

        <div v-if="knowledgeBases.length === 0" class="p-12 text-center">
          <BookOpenIcon class="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <p class="text-slate-500 mb-4">还没有创建任何知识库</p>
          <button
            @click="showCreateModal = true"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
          >
            创建第一个知识库
          </button>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="kb in knowledgeBases"
            :key="kb.id"
            class="p-6 hover:bg-slate-50 transition"
            :class="{ 'bg-primary-50 ring-2 ring-primary-500 ring-inset': currentKB?.id === kb.id }"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1" @click="selectKB(kb.id)">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center cursor-pointer">
                    <BookOpenIcon class="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 class="font-medium text-slate-800">{{ kb.name }}</h3>
                    <p class="text-sm text-slate-500">{{ kb.description || '暂无描述' }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-4 ml-13">
                  <span class="text-sm text-slate-500">
                    <DocumentIcon class="w-4 h-4 inline mr-1" />
                    {{ kb.document_count }} 个文档
                  </span>
                  <span class="text-sm text-slate-500">
                    创建于 {{ formatDate(kb.created_at) }}
                  </span>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <button
                  @click="selectKB(kb.id)"
                  class="p-2 hover:bg-slate-100 rounded-lg transition"
                  title="查看文档"
                >
                  <EyeIcon class="w-5 h-5 text-slate-400" />
                </button>
                <button
                  @click="showDeleteConfirm(kb)"
                  class="p-2 hover:bg-red-50 rounded-lg transition"
                  title="删除"
                >
                  <TrashIcon class="w-5 h-5 text-slate-400 hover:text-red-500" />
                </button>
              </div>
            </div>

            <!-- Documents -->
            <div v-if="currentKB?.id === kb.id" class="mt-6 pt-6 border-t border-slate-200 ml-13">
              <DocumentUploader
                :kb-id="kb.id"
                :uploading="uploading"
                @upload="handleUpload"
              />

              <DocumentList
                :documents="currentKBDocuments"
                @delete="handleDeleteDocument"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <CreateKBModal
      :show="showCreateModal"
      @close="showCreateModal = false"
      @create="handleCreateKB"
    />

    <!-- Delete Confirm Modal -->
    <ConfirmModal
      :show="showDeleteModal"
      :title="`删除知识库 \"${kbToDelete?.name}\"?`"
      :message="'删除后无法恢复，确定要继续吗？'"
      @close="showDeleteModal = false"
      @confirm="handleDeleteKB"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useKnowledgeBaseStore } from '../stores/knowledgeBase'
import {
  ArrowLeftIcon,
  PlusIcon,
  BookOpenIcon,
  DocumentIcon,
  EyeIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'
import CreateKBModal from '../components/kb/CreateKBModal.vue'
import ConfirmModal from '../components/common/ConfirmModal.vue'
import DocumentUploader from '../components/kb/DocumentUploader.vue'
import DocumentList from '../components/kb/DocumentList.vue'

const kbStore = useKnowledgeBaseStore()

const {
  knowledgeBases,
  currentKB,
  totalDocuments,
  currentKBDocuments,
  uploading,
  fetchKnowledgeBases,
  createKnowledgeBase,
  deleteKnowledgeBase,
  selectKB,
  uploadDocument,
  deleteDocument,
} = kbStore

const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const kbToDelete = ref<ReturnType<typeof knowledgeBases>[number] | null>(null)

async function handleCreateKB(name: string, description: string) {
  try {
    await createKnowledgeBase(name, description)
    showCreateModal.value = false
  } catch (error) {
    alert('创建知识库失败，请重试')
  }
}

function showDeleteConfirm(kb: any) {
  kbToDelete.value = kb
  showDeleteModal.value = true
}

async function handleDeleteKB() {
  if (kbToDelete.value) {
    try {
      await deleteKnowledgeBase(kbToDelete.value.id)
      showDeleteModal.value = false
      kbToDelete.value = null
    } catch (error) {
      alert('删除知识库失败，请重试')
    }
  }
}

async function handleUpload(kbId: number, file: File) {
  try {
    await uploadDocument(kbId, file)
  } catch (error) {
    alert('上传文档失败，请重试')
  }
}

async function handleDeleteDocument(kbId: number, docId: string) {
  try {
    await deleteDocument(kbId, docId)
  } catch (error) {
    alert('删除文档失败，请重试')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchKnowledgeBases()
})
</script>

<style scoped>
.ml-13 {
  margin-left: 52px;
}
</style>
