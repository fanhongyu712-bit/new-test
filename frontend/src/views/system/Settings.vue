<template>
  <div class="settings">
    <el-card>
      <template #header>系统设置</template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="系统名称">
          <el-input v-model="form.systemName" />
        </el-form-item>
        <el-form-item label="预警通知">
          <el-switch v-model="form.alertNotification" />
        </el-form-item>
        <el-form-item label="数据刷新间隔">
          <el-select v-model="form.refreshInterval">
            <el-option label="5秒" :value="5" />
            <el-option label="10秒" :value="10" />
            <el-option label="30秒" :value="30" />
            <el-option label="1分钟" :value="60" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const form = ref({
  systemName: '养老机构健康监测与风险预警系统',
  alertNotification: true,
  refreshInterval: 10
})

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}
</script>

<style scoped>
.settings {
  padding: 20px;
}
</style>
