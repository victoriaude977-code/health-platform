<template>
  <div v-loading="loading">
    <h1 class="page-title">Today's Overview</h1>
    <p class="page-subtitle">{{ todayLabel }} · {{ greeting }}</p>

    <!-- Goal banner -->
    <el-card v-if="goal" class="goal-card" shadow="never">
      <div class="goal-card-inner">
        <div class="goal-info">
          <div class="goal-type">
            <el-tag :type="goalTagType" effect="dark" round>
              {{ goalLabel(goal.goal_type) }}
            </el-tag>
            <span v-if="goal.target_weight" class="muted target-text">
              Target: {{ goal.target_weight }} kg
            </span>
          </div>
          <div class="calorie-line" v-if="daily">
            <span class="big-number">{{ daily.remaining !== null ? formatNum(daily.remaining) : '—' }}</span>
            <span class="muted"> kcal remaining today</span>
          </div>
        </div>
        <div class="goal-progress" v-if="daily && daily.daily_target">
          <el-progress type="dashboard" :percentage="progressPct" :width="110"
            :stroke-width="10" :color="progressColor">
            <template #default>
              <div class="progress-label">{{ progressPct }}%</div>
              <div class="muted progress-sublabel">of {{ daily.daily_target }} kcal</div>
            </template>
          </el-progress>
        </div>
      </div>
    </el-card>

    <el-card v-else class="goal-card no-goal" shadow="never">
      <div>
        <b>Set your fitness goal</b>
        <p class="muted" style="margin: 6px 0 14px">
          A goal unlocks personalized calorie targets and recommendations.
        </p>
        <el-button type="primary" @click="$router.push('/goal')">Set goal now</el-button>
      </div>
    </el-card>

    <!-- Stat tiles -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :md="6" v-for="tile in tiles" :key="tile.label">
        <el-card shadow="never" class="stat-tile">
          <div class="stat-label">{{ tile.label }}</div>
          <div class="stat-value" :style="{ color: tile.color }">
            {{ tile.value }}<span class="stat-unit">{{ tile.unit }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- Today's meals -->
      <el-col :xs="24" :lg="12" class="stack-col">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <b>Today's Meals</b>
              <el-button type="primary" link @click="$router.push('/meals')">
                + Log meal
              </el-button>
            </div>
          </template>
          <el-empty v-if="!meals.length" description="Nothing logged yet" :image-size="70" />
          <ul v-else class="log-list">
            <li v-for="m in meals" :key="m.id">
              <div class="log-main">
                <el-tag size="small" effect="plain" :class="`tag-meal-${m.meal_type}`">
                  {{ m.meal_type }}
                </el-tag>
                <span class="log-name">{{ m.food_name }} ×{{ m.quantity }}</span>
              </div>
              <div class="log-side">
                <span class="log-kcal">{{ formatNum(m.calories) }} kcal</span>
                <el-button link type="danger" size="small"
                  @click="removeMeal(m.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </li>
          </ul>
        </el-card>
      </el-col>

      <!-- Today's workouts + macros -->
      <el-col :xs="24" :lg="12" class="stack-col">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <b>Today's Workouts</b>
              <el-button type="primary" link @click="$router.push('/workouts')">
                + Log workout
              </el-button>
            </div>
          </template>
          <el-empty v-if="!workouts.length" description="No workouts yet" :image-size="70" />
          <ul v-else class="log-list">
            <li v-for="w in workouts" :key="w.id">
              <div class="log-main">
                <el-tag size="small" effect="plain">{{ w.category }}</el-tag>
                <span class="log-name">{{ w.exercise_name }} · {{ w.duration_min }} min</span>
              </div>
              <div class="log-side">
                <span class="log-kcal">−{{ formatNum(w.calories_burned) }} kcal</span>
                <el-button link type="danger" size="small"
                  @click="removeWorkout(w.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </li>
          </ul>
          <el-divider v-if="daily && daily.macros" />
          <div v-if="daily && daily.macros" class="macro-row">
            <div class="macro-item">
              <span class="macro-dot" style="background:#14b8a6"></span>
              Protein {{ formatNum(daily.macros.protein) }}g
            </div>
            <div class="macro-item">
              <span class="macro-dot" style="background:#f59e0b"></span>
              Carbs {{ formatNum(daily.macros.carbs) }}g
            </div>
            <div class="macro-item">
              <span class="macro-dot" style="background:#6366f1"></span>
              Fat {{ formatNum(daily.macros.fat) }}g
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recommendation teaser -->
    <el-card shadow="never" class="rec-teaser">
      <template #header>
        <div class="card-header">
          <b>✨ Personalized picks for you</b>
          <el-button type="primary" link @click="$router.push('/recommendations')">
            See all →
          </el-button>
        </div>
      </template>
      <div v-loading="recsLoading">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" v-for="(rec, i) in recs" :key="rec.rec_type + rec.item_id">
            <div class="rec-card">
              <div class="rec-head">
                <el-tag size="small" :type="rec.rec_type === 'meal' ? 'success' : 'warning'"
                  effect="light" round>
                  {{ rec.rec_type === 'meal' ? 'Meal' : 'Workout' }}
                </el-tag>
                <span class="rec-name">{{ rec.item_name }}</span>
              </div>
              <div class="rec-reason">{{ rec.reason }}</div>
            </div>
          </el-col>
        </el-row>
        <el-empty v-if="!recsLoading && !recs.length" description="Log a few meals to get started"
          :image-size="70" />
      </div>
    </el-card>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { getRecommendationHistory } from '@/api/recommendations'
import { deleteMeal } from '@/api/meals'
import { deleteWorkout } from '@/api/workouts'
import { ElMessage } from 'element-plus'

export default {
  name: 'DashboardView',
  setup() {
    const store = useStore()
    const loading = ref(true)
    const recsLoading = ref(true)
    const recs = ref([])

    const goal = computed(() => store.getters['health/activeGoal'])
    const daily = computed(() => store.getters['health/daily'])
    const meals = computed(() => store.state.health.todayMeals)
    const workouts = computed(() => store.state.health.todayWorkouts)
    const user = computed(() => store.getters['auth/user'])

    const today = new Date()
    const todayISO = today.toISOString().slice(0, 10)
    const todayLabel = today.toLocaleDateString('en-US', {
      weekday: 'long', month: 'long', day: 'numeric',
    })
    const greeting = computed(() => {
      const h = new Date().getHours()
      const name = user.value ? user.value.username : ''
      const part = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening'
      return `${part}, ${name}`
    })

    const goalLabel = (t) => ({ lose: 'Lose weight', gain: 'Gain muscle', maintain: 'Maintain' }[t] || t)
    const goalTagType = computed(() => ({ lose: 'danger', gain: 'success', maintain: 'primary' }[goal.value && goal.value.goal_type] || 'info'))
    const progressPct = computed(() => {
      if (!daily.value || !daily.value.daily_target) return 0
      return Math.min(Math.round((daily.value.calories_in / daily.value.daily_target) * 100), 999)
    })
    const progressColor = computed(() => {
      if (!daily.value || !daily.value.daily_target) return '#14b8a6'
      if (daily.value.calories_in > daily.value.daily_target) return '#ef4444'
      if (progressPct.value >= 85) return '#f59e0b'
      return '#14b8a6'
    })

    // Colors are CSS variables so they flip with the theme (inline styles
    // cannot be overridden by html.dark rules).
    const tiles = computed(() => [
      {
        label: 'Calories in',
        value: daily.value ? formatNum(daily.value.calories_in) : '—',
        unit: 'kcal', color: 'var(--brand-dark)',
      },
      {
        label: 'Calories burned',
        value: daily.value ? formatNum(daily.value.calories_out) : '—',
        unit: 'kcal', color: '#f97316',
      },
      {
        label: 'Net',
        value: daily.value ? formatNum(daily.value.net) : '—',
        unit: 'kcal', color: 'var(--ink-strong)',
      },
      {
        label: 'Daily target',
        value: daily.value && daily.value.daily_target ? formatNum(daily.value.daily_target) : '—',
        unit: 'kcal', color: 'var(--brand)',
      },
    ])

    const formatNum = (n) => Math.round(n).toLocaleString('en-US')

    const loadRecs = async () => {
      recsLoading.value = true
      try {
        // Teaser reuses the most recent stored recommendations (no regeneration).
        const { data } = await getRecommendationHistory()
        recs.value = data.items.slice(0, 6)
      } catch {
        recs.value = []
      } finally {
        recsLoading.value = false
      }
    }

    const refresh = async () => {
      loading.value = true
      try {
        await store.dispatch('health/refreshToday', todayISO)
      } finally {
        loading.value = false
      }
    }

    const removeMeal = async (id) => {
      await deleteMeal(id)
      ElMessage.success('Meal removed')
      refresh()
    }
    const removeWorkout = async (id) => {
      await deleteWorkout(id)
      ElMessage.success('Workout removed')
      refresh()
    }

    onMounted(() => {
      refresh()
      loadRecs()
    })

    return {
      loading, recsLoading, recs, goal, daily, meals, workouts,
      todayLabel, greeting, goalLabel, goalTagType, progressPct, progressColor,
      tiles, formatNum, removeMeal, removeWorkout,
    }
  },
}
</script>

<style scoped>
.goal-card {
  margin-bottom: 16px;
  background: linear-gradient(120deg, #f0fdfa 0%, #ffffff 60%);
}

.goal-card-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.goal-type {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.target-text {
  font-size: 13px;
}

.calorie-line {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.big-number {
  font-size: 34px;
  font-weight: 700;
  color: #0f172a;
}

.goal-progress {
  flex-shrink: 0;
}

.progress-label {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.progress-sublabel {
  font-size: 11px;
}

.no-goal {
  margin-bottom: 16px;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-tile {
  text-align: left;
}

.stat-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
}

.stat-unit {
  font-size: 13px;
  font-weight: 400;
  color: #94a3b8;
  margin-left: 4px;
}

.log-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.log-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid #f1f5f9;
}

.log-list li:last-child {
  border-bottom: none;
}

.log-main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-name {
  font-size: 14px;
}

.log-side {
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-kcal {
  font-size: 13px;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

.macro-row {
  display: flex;
  justify-content: space-around;
}

.macro-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  color: #334155;
}

.macro-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.rec-teaser {
  margin-top: 16px;
}

.rec-card {
  border: 1px solid #eef2f6;
  border-radius: 10px;
  padding: 12px 14px;
  min-height: 92px;
  background: #fbfdfe;
}

.rec-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rec-name {
  font-weight: 600;
  font-size: 14px;
  color: #0f172a;
}

.rec-reason {
  font-size: 12.5px;
  color: #64748b;
  line-height: 1.45;
}

/* Phones: stack the two-column rows and let the goal card wrap. */
@media (max-width: 991px) {
  .stack-col {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .goal-card-inner {
    flex-wrap: wrap;
    gap: 14px;
  }

  .goal-progress {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .stat-tile {
    margin-bottom: 16px;
  }

  .stat-row {
    margin-bottom: 0;
  }

  .rec-card {
    margin-bottom: 16px;
  }

  .big-number {
    font-size: 27px;
  }
}
</style>
