<template>
  <div class="alert-center">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>预警中心</span>
          <el-button type="primary" @click="showRuleDialog = true">
            <el-icon><Setting /></el-icon>
            预警规则
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="预警级别">
          <el-select v-model="searchForm.alert_level" placeholder="请选择" clearable>
            <el-option label="危急" value="critical" />
            <el-option label="高风险" value="high" />
            <el-option label="中风险" value="medium" />
            <el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="误报" value="false_alarm" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchAlertList">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="alertList" v-loading="loading" style="width: 100%">
        <el-table-column prop="elderly_name" label="老人姓名" width="100">
          <template #default="{ row }">
            <span>{{ row.elderly_name || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="预警标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="alert_level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertType(row.alert_level)" effect="dark">
              {{ getAlertLevelText(row.alert_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              link
              @click="handleAlert(row)"
            >
              处理
            </el-button>
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchAlertList"
        @current-change="fetchAlertList"
      />
    </el-card>
    
    <el-dialog v-model="showRuleDialog" title="预警规则管理" width="800px">
      <el-table :data="alertRules" style="width: 100%">
        <el-table-column prop="name" label="规则名称" />
        <el-table-column prop="metric_code" label="指标" width="100" />
        <el-table-column prop="condition_type" label="条件" width="80">
          <template #default="{ row }">
            {{ getConditionText(row.condition_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold_value" label="阈值" width="80" />
        <el-table-column prop="alert_level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertType(row.alert_level)">
              {{ getAlertLevelText(row.alert_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active === 'true'"
              @change="updateRuleStatus(row, $event)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <el-dialog v-model="showHandleDialog" title="处理预警" width="500px">
      <el-form :model="handleForm" label-width="80px">
        <el-form-item label="处理结果">
          <el-input
            v-model="handleForm.result"
            type="textarea"
            :rows="4"
            placeholder="请输入处理结果"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHandleDialog = false">取消</el-button>
        <el-button type="primary" @click="submitHandle">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showDetailDialog" title="预警详情" width="600px">
      <el-descriptions :column="2" border v-if="currentAlert">
        <el-descriptions-item label="老人姓名">{{ currentAlert.elderly_name || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="预警级别">
          <el-tag :type="getAlertType(currentAlert.alert_level)" effect="dark">
            {{ getAlertLevelText(currentAlert.alert_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预警类型">{{ currentAlert.alert_type }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentAlert.status)">
            {{ getStatusText(currentAlert.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预警标题" :span="2">{{ currentAlert.title }}</el-descriptions-item>
        <el-descriptions-item label="预警内容" :span="2">{{ currentAlert.content }}</el-descriptions-item>
        <el-descriptions-item label="指标数值">{{ currentAlert.metric_value }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentAlert.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="处理人" v-if="currentAlert.handler_id">{{ currentAlert.handler_id }}</el-descriptions-item>
        <el-descriptions-item label="处理时间" v-if="currentAlert.handle_time">{{ formatTime(currentAlert.handle_time) }}</el-descriptions-item>
        <el-descriptions-item label="处理结果" :span="2" v-if="currentAlert.handle_result">{{ currentAlert.handle_result }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { alertApi } from '@/api/alert'

const loading = ref(false)
const alertList = ref([])
const alertRules = ref([])
const showRuleDialog = ref(false)
const showHandleDialog = ref(false)
const showDetailDialog = ref(false)
const currentAlert = ref(null)

const searchForm = reactive({
  alert_level: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const handleForm = reactive({
  result: ''
})

const alertLevelMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '危急'
}

const alertTypeMap = {
  low: 'info',
  medium: 'warning',
  high: 'warning',
  critical: 'danger'
}

const statusMap = {
  pending: '待处理',
  processing: '处理中',
  resolved: '已解决',
  false_alarm: '误报'
}

const statusTypeMap = {
  pending: 'danger',
  processing: 'warning',
  resolved: 'success',
  false_alarm: 'info'
}

const conditionMap = {
  gt: '大于',
  lt: '小于',
  gte: '大于等于',
  lte: '小于等于',
  eq: '等于'
}

const getAlertLevelText = (level) => alertLevelMap[level] || level
const getAlertType = (level) => alertTypeMap[level] || 'info'
const getStatusText = (status) => statusMap[status] || status
const getStatusType = (status) => statusTypeMap[status] || 'info'
const getConditionText = (condition) => conditionMap[condition] || condition

const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const fetchAlertList = async () => {
  loading.value = true
  try {
    const response = await alertApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    })
    alertList.value = response?.items || []
    pagination.total = response?.total || 0
  } catch (error) {
    ElMessage.error('获取预警列表失败')
  } finally {
    loading.value = false
  }
}

const fetchAlertRules = async () => {
  try {
    const response = await alertApi.getRules()
    alertRules.value = response || []
  } catch (error) {
    ElMessage.error('获取预警规则失败')
  }
}

const resetSearch = () => {
  searchForm.alert_level = ''
  searchForm.status = ''
  pagination.page = 1
  fetchAlertList()
}

const handleAlert = (row) => {
  currentAlert.value = row
  handleForm.result = ''
  showHandleDialog.value = true
}

const submitHandle = async () => {
  if (!handleForm.result) {
    ElMessage.warning('请输入处理结果')
    return
  }
  
  try {
    await alertApi.handleAlert(currentAlert.value.id, handleForm.result)
    ElMessage.success('处理成功')
    showHandleDialog.value = false
    fetchAlertList()
  } catch (error) {
    ElMessage.error('处理失败')
  }
}

const viewDetail = (row) => {
  currentAlert.value = row
  showDetailDialog.value = true
}

const updateRuleStatus = async (row, isActive) => {
  try {
    await alertApi.updateRule(row.id, isActive ? 'true' : 'false')
    row.is_active = isActive ? 'true' : 'false'
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  fetchAlertList()
  fetchAlertRules()
})
</script>

<style scoped>
.alert-center {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
