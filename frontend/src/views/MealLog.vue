<template>
  <div>
    <h1 class="page-title">Meal Logging</h1>
    <p class="page-subtitle">Log what you ate — nutrition is computed from the food database.</p>

    <el-card shadow="never">
      <el-form inline @submit.prevent="submit">
        <el-form-item label="Date">
          <el-date-picker v-model="date" type="date" value-format="YYYY-MM-DD"
            :clearable="false" style="width: 150px" />
        </el-form-item>
        <el-form-item label="Meal">
          <el-select v-model="form.meal_type" style="width: 140px">
            <el-option label="Breakfast" value="breakfast" />
            <el-option label="Lunch" value="lunch" />
            <el-option label="Dinner" value="dinner" />
            <el-option label="Snack" value="snack" />
          </el-select>
        </el-form-item>
        <el-form-item label="Food" class="food-item">
          <el-select v-model="form.food_id" filterable remote clearable
            :remote-method="searchFood" :loading="searching" placeholder="Search food..."
            style="width: 280px">
            <el-option v-for="f in foodOptions" :key="f.id" :value="f.id"
              :label="`${f.name} · ${f.calories} kcal/${f.serving_size}`">
              <span>{{ f.name }}</span>
              <span class="muted" style="float: right; font-size: 12px">
                {{ f.calories }} kcal · {{ f.serving_size }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Servings">
          <el-input-number v-model="form.quantity" :min="0.1" :max="50" :step="0.5"
            controls-position="right" style="width: 110px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="submit">
            <el-icon style="margin-right: 4px"><Plus /></el-icon> Log
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="selectedFood" class="food-preview">
        <el-tag size="small">{{ selectedFood.category }}</el-tag>
        <span class="muted" style="font-size: 13px">
          {{ selectedFood.name }}: {{ selectedFood.calories }} kcal ·
          P {{ selectedFood.protein }}g · C {{ selectedFood.carbs }}g ·
          F {{ selectedFood.fat }}g per {{ selectedFood.serving_size }}
        </span>
      </div>
      <el-alert v-if="error" :title="error" type="error" :closable="false"
        style="margin-top: 10px" />
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <b>Meals on {{ dateLabel }}</b>
          <span class="muted" v-if="totals">Total: {{ totals.calories }} kcal ·
            P {{ totals.protein }}g · C {{ totals.carbs }}g · F {{ totals.fat }}g</span>
        </div>
      </template>
      <el-empty v-if="!items.length" description="No meals logged for this day"
        :image-size="80" />
      <el-table v-else :data="items" style="width: 100%">
        <el-table-column label="Meal" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :class="`tag-meal-${row.meal_type}`">
              {{ row.meal_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="food_name" label="Food" min-width="180" />
        <el-table-column prop="quantity" label="Servings" width="100" />
        <el-table-column prop="calories" label="kcal" width="90" />
        <el-table-column prop="protein" label="Protein" width="90" />
        <el-table-column prop="carbs" label="Carbs" width="90" />
        <el-table-column prop="fat" label="Fat" width="90" />
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
import { searchFoods } from '@/api/foods'
import { getMeals, logMeal, deleteMeal } from '@/api/meals'
import { errorMessage } from '@/api/http'
import { ElMessage } from 'element-plus'

export default {
  name: 'MealLogView',
  setup() {
    const date = ref(new Date().toISOString().slice(0, 10))
    const items = ref([])
    const foodOptions = ref([])
    const searching = ref(false)
    const saving = ref(false)
    const error = ref('')
    const form = reactive({ food_id: null, meal_type: 'breakfast', quantity: 1 })

    const selectedFood = computed(() =>
      foodOptions.value.find((f) => f.id === form.food_id) || null)

    const totals = computed(() => {
      if (!items.value.length) return null
      return items.value.reduce(
        (acc, m) => {
          acc.calories += m.calories
          acc.protein += m.protein
          acc.carbs += m.carbs
          acc.fat += m.fat
          return acc
        },
        { calories: 0, protein: 0, carbs: 0, fat: 0 }
      )
    })

    const dateLabel = computed(() =>
      new Date(date.value + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric',
      }))

    const searchFood = async (query) => {
      searching.value = true
      try {
        const { data } = await searchFoods({ search: query || '', per_page: 30 })
        foodOptions.value = data.items
      } finally {
        searching.value = false
      }
    }

    const load = async () => {
      const { data } = await getMeals(date.value)
      items.value = data.items
    }

    const submit = async () => {
      error.value = ''
      if (!form.food_id) {
        error.value = 'Choose a food first'
        return
      }
      saving.value = true
      try {
        await logMeal({ ...form, log_date: date.value })
        form.food_id = null
        form.quantity = 1
        await load()
      } catch (err) {
        error.value = errorMessage(err, 'Could not log meal')
      } finally {
        saving.value = false
      }
    }

    const remove = async (id) => {
      await deleteMeal(id)
      ElMessage.success('Meal removed')
      load()
    }

    watch(date, load)
    searchFood('')
    load()

    return {
      date, items, foodOptions, searching, saving, error, form,
      selectedFood, totals, dateLabel, searchFood, submit, remove,
    }
  },
}
</script>

<style scoped>
.food-item :deep(.el-select) {
  min-width: 280px;
}

.food-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
</style>
