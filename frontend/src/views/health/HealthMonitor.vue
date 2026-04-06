<template>
  <div class="health-monitor">
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="老人">
          <el-select v-model="selectedElderly" placeholder="请选择老人" clearable>
            <el-option v-for="item in elderlyList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="指标">
          <el-select v-model="selectedMetric" placeholder="请选择指标" clearable>
            <el-option v-for="item in metrics" :key="item.code" :label="item.name" :value="item.code" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6" v-for="metric in latestData" :key="metric.name">
        <el-card class="metric-card">
          <div class="metric-name">{{ metric.name }}</div>
          <div class="metric-value">{{ metric.value }} <span class="unit">{{ metric.unit }}</span></div>
          <div class="metric-time">{{ formatTime(metric.time) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <div ref="chartRef" class="chart"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { getHealthMetrics, getLatestHealthData, getHealthTrend } from '@/api/health'
import { getElderlyList } from '@/api/elderly'
import dayjs from 'dayjs'

const elderlyList = ref([])
const metrics = ref([])
const selectedElderly = ref('')
const selectedMetric = ref('heart_rate')
const latestData = ref([])
const chartRef = ref(null)
let chart = null

const formatTime = (time) => dayjs(time).format('MM-DD HH:mm')

const fetchElderly = async () => {
  const res = await getElderlyList({ page: 1, page_size: 100 })
  elderlyList.value = res?.items || []
  if (elderlyList.value.length > 0) {
    selectedElderly.value = elderlyList.value[0].id
  }
}

const fetchMetrics = async () => {
  const res = await getHealthMetrics()
  metrics.value = res || []
}

const fetchLatestData = async () => {
  if (!selectedElderly.value) return
  const res = await getLatestHealthData(selectedElderly.value)
  latestData.value = Object.values(res || {})
}

const fetchData = async () => {
  await fetchLatestData()
  if (selectedElderly.value && selectedMetric.value) {
    const res = await getHealthTrend(selectedElderly.value, selectedMetric.value)
    renderChart(res)
  }
}

const renderChart = (data) => {
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  const option = {
    title: { text: data.metric_name + '趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.data.map(d => dayjs(d.time).format('MM-DD HH:mm'))
    },
    yAxis: { type: 'value', name: data.unit },
    series: [{
      type: 'line',
      data: data.data.map(d => d.value),
      smooth: true,
      areaStyle: { opacity: 0.3 }
    }]
  }
  
  chart.setOption(option)
}

onMounted(async () => {
  await Promise.all([fetchElderly(), fetchMetrics()])
  await fetchData()
})
</script>

<style scoped>
.health-monitor {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-name {
  font-size: 14px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin: 10px 0;
}

.metric-value .unit {
  font-size: 14px;
  color: #909399;
}

.metric-time {
  font-size: 12px;
  color: #C0C4CC;
}

.chart-card {
  margin-top: 20px;
}

.chart {
  height: 400px;
}
</style>
