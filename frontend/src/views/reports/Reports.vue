<template>
  <div class="reports">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total_elderly }}</div>
          <div class="stat-label">老人总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning">
          <div class="stat-value">{{ stats.today_alerts }}</div>
          <div class="stat-label">今日预警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card danger">
          <div class="stat-value">{{ stats.pending_alerts }}</div>
          <div class="stat-label">待处理预警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card critical">
          <div class="stat-value">{{ stats.critical_alerts }}</div>
          <div class="stat-label">紧急预警</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>预警级别分布</template>
          <div ref="levelChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>预警状态分布</template>
          <div ref="statusChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px;">
      <template #header>健康风险分布</template>
      <div ref="riskChartRef" class="chart"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats, getAlertStatistics, getHealthOverview } from '@/api/report'

const stats = ref({
  total_elderly: 0,
  today_alerts: 0,
  pending_alerts: 0,
  critical_alerts: 0
})

const levelChartRef = ref(null)
const statusChartRef = ref(null)
const riskChartRef = ref(null)

const fetchStats = async () => {
  const res = await getDashboardStats()
  stats.value = res || {}
}

const fetchAlertStats = async () => {
  const res = await getAlertStatistics()
  const data = res || {}
  
  const levelChart = echarts.init(levelChartRef.value)
  levelChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      data: Object.entries(data.by_level || {}).map(([name, value]) => ({ name, value }))
    }]
  })
  
  const statusChart = echarts.init(statusChartRef.value)
  statusChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      data: Object.entries(data.by_status || {}).map(([name, value]) => ({ name, value }))
    }]
  })
}

const fetchHealthOverview = async () => {
  const res = await getHealthOverview()
  const data = res || {}
  
  const riskChart = echarts.init(riskChartRef.value)
  riskChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      data: Object.entries(data.risk_distribution || {}).map(([name, value]) => ({ name, value }))
    }]
  })
}

onMounted(async () => {
  await fetchStats()
  await Promise.all([fetchAlertStats(), fetchHealthOverview()])
})
</script>

<style scoped>
.reports {
  padding: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card.warning .stat-value {
  color: #E6A23C;
}

.stat-card.danger .stat-value {
  color: #F56C6C;
}

.stat-card.critical .stat-value {
  color: #F56C6C;
}

.stat-label {
  margin-top: 10px;
  color: #909399;
}

.chart {
  height: 300px;
}
</style>
