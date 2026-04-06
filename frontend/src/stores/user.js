import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || '')
  const userName = computed(() => userInfo.value?.real_name || userInfo.value?.username || '')

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  async function login(username, password) {
    try {
      const response = await authApi.login(username, password)
      const { access_token } = response.data || response
      setToken(access_token)
      
      const userResponse = await authApi.getCurrentUser()
      setUserInfo(userResponse.data || userResponse)
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.push('/login')
  }

  function hasRole(roles) {
    if (!roles || roles.length === 0) return true
    return roles.includes(userRole.value)
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userRole,
    userName,
    setToken,
    setUserInfo,
    login,
    logout,
    hasRole
  }
})
