<template>
  <div class="auth-card">
    <h1>Create your account 🌱</h1>
    <p class="subtitle">Track meals & workouts, get personalized recommendations</p>
    <el-form :model="form" label-position="top" @submit.prevent="submit">
      <el-form-item label="Username">
        <el-input v-model="form.username" placeholder="e.g. alex" size="large" />
      </el-form-item>
      <el-form-item label="Email">
        <el-input v-model="form.email" placeholder="you@example.com" size="large" />
      </el-form-item>
      <el-form-item label="Password (min 6 characters)">
        <el-input v-model="form.password" type="password" size="large" show-password />
      </el-form-item>
      <el-collapse class="optional-profile">
        <el-collapse-item title="Body profile (optional — needed for calorie targets)">
          <div class="row">
            <el-form-item label="Height (cm)">
              <el-input-number v-model="form.height" :min="50" :max="250" :step="1"
                controls-position="right" />
            </el-form-item>
            <el-form-item label="Weight (kg)">
              <el-input-number v-model="form.weight" :min="20" :max="400" :step="0.5"
                controls-position="right" />
            </el-form-item>
          </div>
          <div class="row">
            <el-form-item label="Age">
              <el-input-number v-model="form.age" :min="10" :max="100" :step="1"
                controls-position="right" />
            </el-form-item>
            <el-form-item label="Gender">
              <el-select v-model="form.gender" placeholder="Select">
                <el-option label="Female" value="female" />
                <el-option label="Male" value="male" />
                <el-option label="Other" value="other" />
              </el-select>
            </el-form-item>
          </div>
        </el-collapse-item>
      </el-collapse>
      <el-alert v-if="error" :title="error" type="error" :closable="false" class="alert" />
      <el-button type="primary" size="large" class="submit" :loading="loading"
        @click="submit">
        Sign up
      </el-button>
    </el-form>
    <div class="footer">
      <span class="muted">Already have an account?</span>
      <router-link to="/login">Sign in</router-link>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { errorMessage } from '@/api/http'

export default {
  name: 'RegisterView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const form = reactive({
      username: '', email: '', password: '',
      height: null, weight: null, age: null, gender: '',
    })
    const loading = ref(false)
    const error = ref('')

    const submit = async () => {
      error.value = ''
      if (!form.username || !form.email || !form.password) {
        error.value = 'Username, email and password are required'
        return
      }
      loading.value = true
      try {
        const payload = { ...form }
        // element-plus number inputs keep nulls - convert for the API.
        for (const k of ['height', 'weight', 'age']) {
          if (payload[k] == null) delete payload[k]
        }
        if (!payload.gender) delete payload.gender
        await store.dispatch('auth/register', payload)
        // New users land on Profile (with the welcome banner) to pick an
        // avatar and complete their body profile before anything else.
        router.push('/profile?welcome=1')
      } catch (err) {
        error.value = errorMessage(err, 'Registration failed')
      } finally {
        loading.value = false
      }
    }
    return { form, loading, error, submit }
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

.optional-profile {
  margin-bottom: 8px;
  border: none;
}

.row {
  display: flex;
  gap: 16px;
}

.row .el-form-item {
  flex: 1;
}

@media (max-width: 480px) {
  .row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
