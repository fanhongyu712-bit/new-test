<template>
  <div class="profile">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>个人信息</template>
          <div class="user-avatar">
            <el-avatar :size="80" icon="UserFilled" />
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ userInfo.real_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ userInfo.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ userInfo.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ getRoleText(userInfo.role) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="userInfo.status === 'active' ? 'success' : 'danger'">
                {{ userInfo.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>修改信息</template>
          <el-form :model="form" label-width="80px" style="max-width: 500px;">
            <el-form-item label="姓名">
              <el-input v-model="form.real_name" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="电话">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>修改密码</template>
          <el-form :model="passwordForm" label-width="100px" style="max-width: 500px;">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const userInfo = ref({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: '',
  status: ''
})

const form = reactive({
  real_name: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const getRoleText = (role) => {
  const texts = { admin: '管理员', doctor: '医生', nurse: '护士', institution_admin: '机构管理员' }
  return texts[role] || role
}

const loadUserInfo = () => {
  const user = userStore.userInfo
  if (user) {
    userInfo.value = { ...user }
    form.real_name = user.real_name || ''
    form.email = user.email || ''
    form.phone = user.phone || ''
  }
}

const saveProfile = () => {
  userInfo.value.real_name = form.real_name
  userInfo.value.email = form.email
  userInfo.value.phone = form.phone
  ElMessage.success('保存成功')
}

const changePassword = () => {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次密码不一致')
    return
  }
  ElMessage.success('密码修改成功')
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile {
  padding: 20px;
}

.user-avatar {
  text-align: center;
  margin-bottom: 20px;
}
</style>
