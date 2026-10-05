<template>
  <div>
    <h1 class="page-title">Workout Logging</h1>
    <p class="page-subtitle">
      Calories burned are computed automatically: MET × body weight × duration.
    </p>

    <el-card shadow="never">
      <el-form inline @submit.prevent="submit">
        <el-form-item label="Date">
          <el-date-picker v-model="date" type="date" value-format="YYYY-MM-DD"
            :clearable="false" style="width: 150px" />
        </el-form-item>
        <el-form-item label="Exercise">
          <el-select v-model="form.exercise_id" filterable remote clearable
            :remote-method="searchExercise" :loading="searching" placeholder="Search exercise..."
            style="width: 260px">
            <el-option v-for="e in exerciseOptions" :key="e.id" :value="e.id"
              :label="`${e.name} (MET ${e.met_value})`">
              <span>{{ e.name }}</span>
              <span class="muted" style="float: right; font-size: 12px">
                {{ e.category }} · MET {{ e.met_value }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Duration (min)">
          <el-input-number v-model="form.duration_min" :min="1" :max="1440" :step="5"
            controls-position="right" style="width: 120px" />
        </el-form-item>
        <el-form-item label="Intensity">
          <el-select v-model="form.intensity" style="width: 130px">
            <el-option label="Light" value="light" />
            <el-option label="Moderate" value="moderate" />
            <el-option label="Vigorous" value="vigorous" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="submit">
            <el-icon style="margin-right: 4px"><Plus /></el-icon> Log
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="estimate" class="muted" style="font-size: 13px">
        Estimated burn: <b style="color: #f97316">{{ estimate }} kcal</b>
        <template v-if="!hasWeight"> (set your weight in Profile for a precise value)</template>
      </div>
      <el-alert v-if="error" :title="error" type="error" :closable="false"
        style="margin-top: 10px" />
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <b>Workouts on {{ dateLabel }}</b>
          <span class="muted" v-if="items.length">
            Total burned: {{ totalBurned }} kcal
          </span>
        </div>
      </template>
      <el-empty v-if="!items.length" description="No workouts logged for this day"
        :image-size="80" />
      <el-table v-else :data="items" style="width: 100%">
        <el-table-column prop="exercise_name" label="Exercise" min-width="180" />
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="duration_min" label="Duration" width="100" />
        <el-table-column prop="intensity" label="Intensity" width="110" />
        <el-table-column label="Burned" width="110">
          <template #default="{ row }">
            <b style="color: #f97316">{{ row.calories_burned }} kcal</b>
          </template>
        </el-table-column>
        <el-table-column label="" width="70" align="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="remove(row.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { computed, reactive, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { searchExercises } from '@/api/exercises'
import { getWorkouts, logWorkout, deleteWorkout } from '@/api/workouts'
import { errorMessage } from '@/api/http'
import { ElMessage } from 'element-plus'

const INTENSITY_FACTORS = { light: 0.85, moderate: 1.0, vigorous: 1.2 }

export default {
  name: 'WorkoutLogView',
  setup() {
    const store = useStore()
    const date = ref(new Date().toISOString().slice(0, 10))
    const items = ref([])
    const exerciseOptions = ref([])
    const searching = ref(false)
    const saving = ref(false)
    const error = ref('')
    const form = reactive({ exercise_id: null, duration_min: 30, intensity: 'moderate' })

    const user = computed(() => store.getters['auth/user'])
    const hasWeight = computed(() => Boolean(user.value && user.value.weight))
    const selectedExercise = computed(() =>
      exerciseOptions.value.find((e) => e.id === form.exercise_id) || null)

    const estimate = computed(() => {
      const ex = selectedExercise.value
      if (!ex) return null
      const weight = (user.value && user.value.weight) || 65
      const factor = INTENSITY_FACTORS[form.intensity] || 1
      return Math.round(ex.met_value * weight * (form.duration_min / 60) * factor)
    })

    const totalBurned = computed(() =>
      items.value.reduce((acc, w) => acc + w.calories_burned, 0).toFixed(0))

    const dateLabel = computed(() =>
      new Date(date.value + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric',
      }))

    const searchExercise = async (query) => {
      searching.value = true
      try {
        const { data } = await searchExercises({ search: query || '' })
        exerciseOptions.value = data.items
      } finally {
        searching.value = false
      }
    }

    const load = async () => {
      const { data } = await getWorkouts(date.value)
      items.value = data.items
    }

    const submit = async () => {
      error.value = ''
      if (!form.exercise_id) {
        error.value = 'Choose an exercise first'
        return
      }
      saving.value = true
      try {
        await logWorkout({ ...form, log_date: date.value })
        form.exercise_id = null
        await load()
      } catch (err) {
        error.value = errorMessage(err, 'Could not log workout')
      } finally {
        saving.value = false
      }
    }

    const remove = async (id) => {
      await deleteWorkout(id)
      ElMessage.success('Workout removed')
      load()
    }

    watch(date, load)
    searchExercise('')
    load()

    return {
      date, items, exerciseOptions, searching, saving, error, form,
      hasWeight, estimate, totalBurned, dateLabel, searchExercise, submit, remove,
    }
  },
}
</script>
