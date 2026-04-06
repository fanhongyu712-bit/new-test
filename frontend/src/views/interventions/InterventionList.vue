<template>
  <div class="intervention-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>干预记录列表</span>
        </div>
      </template>
      
      <el-table :data="records" v-loading="loading">
        <el-table-column prop="elderly_id" label="老人ID" width="280" />
        <el-table-column prop="content" label="干预内容" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="effectiveness" label="效果评估" width="100" />
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchRecords"
        @current-change="fetchRecords"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInterventionRecords } from '@/api/alert'
import dayjs from 'dayjs'

const loading = ref(false)
const records = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formatTime = (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'

const getStatusType = (status) => {
  const types = { ongoing: 'warning', completed: 'success', cancelled: 'info' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { ongoing: '进行中', completed: '已完成', cancelled: '已取消' }
  return texts[status] || status
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await getInterventionRecords({ page: page.value, page_size: pageSize.value })
    records.value = res?.items || []
    total.value = res?.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.intervention-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
