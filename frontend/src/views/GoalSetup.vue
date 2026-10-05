<template>
  <div>
    <h1 class="page-title">Your Fitness Goal</h1>
    <p class="page-subtitle">
      The goal drives your daily calorie target and every personalized recommendation.
    </p>

    <el-card shadow="never" v-if="!profileComplete" class="profile-warning">
      <el-alert type="warning" :closable="false" show-icon
        title="Your body profile is incomplete">
        <p style="margin: 6px 0 12px">
          We need your height, weight, age and gender to compute your daily calorie
          target automatically.
        </p>
        <el-button type="primary" size="small" @click="$router.push('/profile')">
          Complete profile
        </el-button>
        <span class="muted" style="margin-left: 12px; font-size: 13px">
          (or enter a calorie target manually below)
        </span>
      </el-alert>
    </el-card>

    <el-card shadow="never">
      <el-form :model="form" label-position="top" style="max-width: 560px">
        <el-form-item label="What's your goal?">
          <el-radio-group v-model="form.goal_type" class="goal-options">
            <el-radio-button value="lose">
              <div class="goal-option">
                <div class="goal-option-title">🔥 Lose weight</div>
                <div class="goal-option-sub">Calorie deficit, high protein</div>
              </div>
            </el-radio-button>
            <el-radio-button value="gain">
              <div class="goal-option">
                <div class="goal-option-title">💪 Gain muscle</div>
                <div class="goal-option-sub">Calorie surplus, strength focus</div>
              </div>
            </el-radio-button>
            <el-radio-button value="maintain">
              <div class="goal-option">
                <div class="goal-option-title">⚖️ Maintain</div>
                <div class="goal-option-sub">Balanced, steady state</div>
              </div>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Target weight (kg, optional)">
          <el-input-number v-model="form.target_weight" :min="30" :max="300"
            :step="0.5" controls-position="right" />
        </el-form-item>

        <el-form-item label="Daily calorie target (kcal)">
          <el-input-number v-model="form.daily_calorie_target" :min="1200" :max="6000"
            :step="50" controls-position="right" placeholder="Auto-computed" />
          <div class="muted" style="font-size: 12.5px; margin-top: 6px">
            <template v-if="estimatedTarget">
              Recommended: <b>{{ estimatedTarget }}</b> kcal/day
              (Mifflin-St Jeor from your profile). Leave blank to use it automatically.
            </template>
            <template v-else>
              Leave blank — we'll compute it from your body profile.
            </template>
          </div>
        </el-form-item>

        <el-form-item label="Duration">
          <el-select v-model="form.duration" style="width: 200px">
            <el-option label="4 weeks" value="4w" />
            <el-option label="8 weeks" value="8w" />
            <el-option label="12 weeks (recommended)" value="12w" />
            <el-option label="24 weeks" value="24w" />
          </el-select>
        </el-form-item>

        <el-alert v-if="error" :title="error" type="error" :closable="false"
          style="margin-bottom: 14px" />

        <div class="actions">
          <el-button type="primary" :loading="saving" @click="save">Save goal</el-button>
          <el-button v-if="activeGoal" @click="cancel">Cancel</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card v-if="activeGoal" shadow="never" style="margin-top: 16px">
      <template #header><b>Current goal</b></template>
      <el-descriptions :column="descCols" border>
        <el-descriptions-item label="Type">{{ goalLabel(activeGoal.goal_type) }}</el-descriptions-item>
        <el-descriptions-item label="Daily target">{{ activeGoal.daily_calorie_target }} kcal</el-descriptions-item>
        <el-descriptions-item label="Target weight">{{ activeGoal.target_weight || '—' }} kg</el-descriptions-item>
        <el-descriptions-item label="Start">{{ activeGoal.start_date }}</el-descriptions-item>
        <el-descriptions-item label="End">{{ activeGoal.end_date }}</el-descriptions-item>
        <el-descriptions-item>
          <el-button link type="danger" @click="removeGoal">Delete goal</el-button>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { createGoal, deleteGoal } from '@/api/goals'
import { errorMessage } from '@/api/http'
import { ElMessage } from 'element-plus'
import { useIsMobile } from '@/composables/useIsMobile'

// Client-side mirror of the backend Mifflin-St Jeor formula (display only;
// the backend always computes the authoritative value).
function estimateTarget(user, goalType) {
  if (!user || !user.height || !user.weight || !user.age || !user.gender) return null
  const base = 10 * user.weight + 6.25 * user.height - 5 * user.age
  const bmr = user.gender === 'male' ? base + 5 : base - 161
  const tdee = bmr * 1.375 // lightly active
  const adj = { lose: -400, gain: 300, maintain: 0 }[goalType]
  return Math.max(Math.round(tdee + adj), 1200)
}

export default {
  name: 'GoalSetupView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const isMobile = useIsMobile()
    const descCols = computed(() => (isMobile.value ? 1 : 3))
    const saving = ref(false)
    const error = ref('')
    const activeGoal = computed(() => store.getters['health/activeGoal'])
    const user = computed(() => store.getters['auth/user'])
    const profileComplete = computed(() => {
      const u = user.value || {}
      return u.height && u.weight && u.age && u.gender
    })

    const form = reactive({
      goal_type: 'lose',
      target_weight: null,
      daily_calorie_target: null,
      duration: '12w',
    })

    const estimatedTarget = computed(() =>
      estimateTarget(user.value, form.goal_type))

    const goalLabel = (t) => ({ lose: 'Lose weight', gain: 'Gain muscle', maintain: 'Maintain' }[t] || t)

    onMounted(() => {
      store.dispatch('health/fetchGoal').catch(() => {})
      if (activeGoal.value) {
        form.goal_type = activeGoal.value.goal_type
        form.target_weight = activeGoal.value.target_weight
        form.daily_calorie_target = activeGoal.value.daily_calorie_target
      }
    })

    const save = async () => {
      error.value = ''
      saving.value = true
      try {
        const weeks = parseInt(form.duration.replace('w', ''), 10)
        const start = new Date()
        const end = new Date()
        end.setDate(end.getDate() + weeks * 7)
        const payload = {
          goal_type: form.goal_type,
          target_weight: form.target_weight,
          daily_calorie_target: form.daily_calorie_target,
          start_date: start.toISOString().slice(0, 10),
          end_date: end.toISOString().slice(0, 10),
        }
        if (payload.daily_calorie_target == null) delete payload.daily_calorie_target
        await createGoal(payload)
        await store.dispatch('health/fetchGoal')
        ElMessage.success('Goal saved — recommendations are now personalized')
        router.push('/')
      } catch (err) {
        error.value = errorMessage(err, 'Could not save goal')
      } finally {
        saving.value = false
      }
    }

    const removeGoal = async () => {
      if (!activeGoal.value) return
      await deleteGoal(activeGoal.value.id)
      await store.dispatch('health/fetchGoal')
      ElMessage.success('Goal deleted')
    }

    const cancel = () => router.push('/')

    return {
      form, saving, error, activeGoal, profileComplete, estimatedTarget,
      goalLabel, save, removeGoal, cancel, descCols,
    }
  },
}
</script>

<style scoped>
.profile-warning {
  margin-bottom: 16px;
}

.goal-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.goal-options :deep(.el-radio-button) {
  flex: 1;
  min-width: 150px;
}

.goal-options :deep(.el-radio-button__inner) {
  height: auto;
  width: 100%;
  padding: 14px 18px;
  border-radius: 10px !important;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.goal-option-title {
  font-weight: 600;
  margin-bottom: 3px;
}

.goal-option-sub {
  font-size: 12px;
  color: #64748b;
}

.actions {
  margin-top: 8px;
}
</style>
