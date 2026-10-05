<template>
  <div>
    <h1 class="page-title">My Profile</h1>
    <p class="page-subtitle">
      Your body profile powers calorie targets (Mifflin-St Jeor) and workout burn
      estimates (MET × weight).
    </p>

    <!-- Shown right after registration -->
    <el-card v-if="welcome" class="welcome-card" shadow="never">
      <div class="welcome-inner">
        <div>
          <b>🎉 Account created — welcome aboard!</b>
          <p class="muted" style="margin: 6px 0 0">
            Pick an avatar and complete your body profile below. Done? Set a goal
            to unlock personalized calorie targets and recommendations.
          </p>
        </div>
        <el-button type="primary" @click="$router.push('/goal')">
          Set my goal →
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="16">
      <!-- Avatar -->
      <el-col :xs="24" :md="10">
        <el-card shadow="never" class="avatar-card">
          <template #header><b>Avatar</b></template>

          <div class="avatar-center">
            <UserAvatar :avatar="avatar" :username="user.username" :size="84" />
          </div>

          <div class="avatar-picker">
            <button v-for="p in PRESET_AVATARS" :key="p.key" type="button"
              class="preset" :class="{ selected: avatar === 'preset:' + p.key }"
              :style="{ background: p.bg }" :title="p.key"
              @click="pickPreset(p.key)">
              {{ p.emoji }}
            </button>
          </div>

          <div class="avatar-actions">
            <el-upload :show-file-list="false" :http-request="doUpload"
              accept="image/png,image/jpeg,image/webp,image/gif">
              <el-button size="small" :loading="uploading">
                <el-icon style="margin-right: 4px"><Camera /></el-icon>
                Upload picture
              </el-button>
            </el-upload>
            <el-button v-if="avatar" size="small" @click="clearAvatar">
              Remove
            </el-button>
          </div>
          <p class="muted avatar-hint">Pick an icon, or upload your own picture (PNG / JPG / WebP / GIF, max 2 MB).</p>
        </el-card>
      </el-col>

      <!-- Body profile -->
      <el-col :xs="24" :md="14">
        <el-card shadow="never">
          <template #header><b>Body profile</b></template>
          <el-form :model="form" label-position="top">
            <el-row :gutter="14">
              <el-col :xs="12">
                <el-form-item label="Height (cm)">
                  <el-input-number v-model="form.height" :min="50" :max="250" :step="1"
                    controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="12">
                <el-form-item label="Weight (kg)">
                  <el-input-number v-model="form.weight" :min="20" :max="400" :step="0.5"
                    controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="12">
                <el-form-item label="Age">
                  <el-input-number v-model="form.age" :min="10" :max="100" :step="1"
                    controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="12">
                <el-form-item label="Gender">
                  <el-select v-model="form.gender" style="width: 100%">
                    <el-option label="Female" value="female" />
                    <el-option label="Male" value="male" />
                    <el-option label="Other" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-button type="primary" :loading="saving" @click="save">
              Save profile
            </el-button>
          </el-form>
        </el-card>

        <el-card shadow="never" class="account-card">
          <template #header><b>Account</b></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Username">{{ user.username }}</el-descriptions-item>
            <el-descriptions-item label="Email">{{ user.email }}</el-descriptions-item>
            <el-descriptions-item label="Joined">
              {{ new Date(user.created_at).toLocaleDateString('en-US') }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { updateProfile, uploadAvatar } from '@/api/profile'
import { errorMessage } from '@/api/http'
import { ElMessage } from 'element-plus'
import { PRESET_AVATARS } from '@/constants/avatars'
import UserAvatar from '@/components/UserAvatar.vue'

export default {
  name: 'ProfileView',
  components: { UserAvatar },
  setup() {
    const store = useStore()
    const route = useRoute()
    const user = computed(() => store.getters['auth/user'] || {})
    const avatar = computed(() => user.value.avatar || null)
    const welcome = computed(() => route.query.welcome === '1')
    const saving = ref(false)
    const uploading = ref(false)
    const form = reactive({
      height: user.value.height,
      weight: user.value.weight,
      age: user.value.age,
      gender: user.value.gender || '',
    })

    const refreshUser = () => store.dispatch('auth/fetchMe')

    const pickPreset = async (key) => {
      try {
        await updateProfile({ avatar: `preset:${key}` })
        await refreshUser()
        ElMessage.success('Avatar updated')
      } catch (err) {
        ElMessage.error(errorMessage(err, 'Could not update avatar'))
      }
    }

    const clearAvatar = async () => {
      try {
        await updateProfile({ avatar: '' })
        await refreshUser()
        ElMessage.success('Avatar removed')
      } catch (err) {
        ElMessage.error(errorMessage(err, 'Could not remove avatar'))
      }
    }

    // el-upload custom request: send multipart through our axios instance so
    // the JWT header is attached automatically.
    const doUpload = async (options) => {
      uploading.value = true
      try {
        const fd = new FormData()
        fd.append('file', options.file)
        await uploadAvatar(fd)
        await refreshUser()
        ElMessage.success('Picture uploaded')
      } catch (err) {
        ElMessage.error(errorMessage(err, 'Could not upload picture'))
      } finally {
        uploading.value = false
      }
    }

    const save = async () => {
      saving.value = true
      try {
        const payload = { ...form }
        if (!payload.gender) delete payload.gender
        await updateProfile(payload)
        await refreshUser()
        ElMessage.success('Profile updated')
      } catch (err) {
        ElMessage.error(errorMessage(err, 'Could not update profile'))
      } finally {
        saving.value = false
      }
    }

    return {
      user, avatar, welcome, form, saving, uploading,
      PRESET_AVATARS, pickPreset, clearAvatar, doUpload, save,
    }
  },
}
</script>

<style scoped>
.welcome-card {
  margin-bottom: 16px;
  background: linear-gradient(120deg, #ecfdf5 0%, var(--surface) 55%);
}

.welcome-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.avatar-card {
  margin-bottom: 16px;
}

.avatar-center {
  display: flex;
  justify-content: center;
  margin-bottom: 18px;
}

.avatar-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 18px;
}

.preset {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s, border-color 0.12s;
}

.preset:hover {
  transform: scale(1.08);
}

.preset.selected {
  border-color: var(--brand);
}

.avatar-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.avatar-hint {
  text-align: center;
  font-size: 12px;
  margin: 12px 0 0;
}

.account-card {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .welcome-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
