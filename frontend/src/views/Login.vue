<template>
  <div class="auth-card">
    <h1>Welcome back 👋</h1>
    <p class="subtitle">Sign in to your health dashboard</p>
    <el-form :model="form" @submit.prevent="submit">
      <el-form-item>
        <el-input v-model="form.identifier" placeholder="Username or email" size="large"
          :prefix-icon="User" />
      </el-form-item>
      <el-form-item>
        <el-input v-model="form.password" type="password" placeholder="Password" size="large"
          :prefix-icon="Lock" show-password @keyup.enter="submit" />
      </el-form-item>
      <el-alert v-if="error" :title="error" type="error" :closable="false" class="alert" />
      <el-button type="primary" size="large" class="submit" :loading="loading"
        @click="submit">
        Sign in
      </el-button>
    </el-form>
    <div class="footer">
      <span class="muted">No account?</span>
      <router-link to="/register">Create one</router-link>
    </div>
    <el-divider class="demo-divider">
      <span class="muted demo-hint">Demo: username <b>demo</b> / password <b>demo1234</b></span>
    </el-divider>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { User, Lock } from '@element-plus/icons-vue'
import { errorMessage } from '@/api/http'

export default {
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const form = reactive({ identifier: '', password: '' })
    const loading = ref(false)
    const error = ref('')

    const submit = async () => {
      error.value = ''
      if (!form.identifier || !form.password) {
        error.value = 'Please fill in both fields'
        return
      }
      loading.value = true
      try {
        await store.dispatch('auth/login', {
          username: form.identifier,
          password: form.password,
        })
        router.push(route.query.redirect || '/')
      } catch (err) {
        error.value = errorMessage(err, 'Login failed')
      } finally {
        loading.value = false
      }
    }
    return { form, loading, error, submit, User, Lock }
  },
}
</script>

<style scoped>
.submit {
  width: 100%;
  margin-top: 6px;
  font-weight: 600;
}

.alert {
  margin-bottom: 14px;
}

.footer {
  margin-top: 18px;
  display: flex;
  gap: 6px;
  justify-content: center;
  font-size: 14px;
}

.demo-divider {
  margin: 22px 0 0;
}

.demo-hint {
  font-size: 12px;
}
</style>
