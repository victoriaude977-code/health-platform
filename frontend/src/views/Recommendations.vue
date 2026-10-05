<template>
  <div>
    <h1 class="page-title">Personalized For You ✨</h1>
    <p class="page-subtitle">
      Hybrid recommendation engine: collaborative filtering when you have enough
      history, content-based fallback while you're new — every pick explained.
    </p>

    <el-card shadow="never">
      <div class="rec-toolbar">
        <el-radio-group v-model="recType" @change="load">
          <el-radio-button value="meal">🍽️ Meal ideas</el-radio-button>
          <el-radio-button value="workout">🏃 Workout ideas</el-radio-button>
        </el-radio-group>
        <el-button :loading="loading" @click="load">
          <el-icon style="margin-right: 4px"><Refresh /></el-icon> Refresh
        </el-button>
      </div>

      <el-alert v-if="strategyInfo" :type="strategyInfo.type" :closable="false"
        show-icon class="strategy-banner" :title="strategyInfo.title">
        <div class="muted" style="font-size: 12.5px">{{ strategyInfo.detail }}</div>
      </el-alert>

      <div v-loading="loading">
        <el-empty v-if="!loading && !items.length"
          :description="`No ${recType} recommendations yet — log some data first`"
          :image-size="90" />
        <div class="rec-grid">
          <div v-for="(rec, i) in items" :key="rec.item_id" class="rec-card">
            <div class="rec-rank">{{ i + 1 }}</div>
            <div class="rec-body">
              <div class="rec-title-row">
                <span class="rec-name">{{ rec.name }}</span>
                <el-tag size="small" effect="plain">{{ rec.category }}</el-tag>
              </div>
              <div class="rec-reason">💡 {{ rec.reason }}</div>
              <div v-if="recType === 'meal'" class="rec-nutrition">
                <span>{{ Math.round(rec.calories) }} kcal</span>
                <span>P {{ rec.protein }}g</span>
                <span>C {{ rec.carbs }}g</span>
                <span>F {{ rec.fat }}g</span>
                <span class="muted">· {{ rec.serving_size }}</span>
              </div>
              <div v-else class="rec-nutrition">
                <span>MET {{ rec.met_value }}</span>
                <span class="muted">· moderate 30 min ≈
                  {{ Math.round(rec.met_value * (userWeight || 65) * 0.5) }} kcal</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <b>Recommendation history</b>
          <span class="muted">Stored with a reason for explainability</span>
        </div>
      </template>
      <el-empty v-if="!history.length" description="No history yet" :image-size="70" />
      <el-table v-else :data="history" size="small" max-height="320">
        <el-table-column prop="created_at" label="When" width="170">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('en-US') }}
          </template>
        </el-table-column>
        <el-table-column prop="rec_type" label="Type" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.rec_type === 'meal' ? 'success' : 'warning'"
              effect="light" round>
              {{ row.rec_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="item_name" label="Item" width="200" />
        <el-table-column prop="reason" label="Why" min-width="260" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { getRecommendations, getRecommendationHistory } from '@/api/recommendations'

export default {
  name: 'RecommendationsView',
  setup() {
    const store = useStore()
    const recType = ref('meal')
    const items = ref([])
    const history = ref([])
    const strategy = ref('')
    const loading = ref(false)

    const userWeight = computed(() => {
      const u = store.getters['auth/user']
      return u && u.weight ? u.weight : null
    })

    const strategyInfo = computed(() => {
      if (strategy.value === 'cf') {
        return {
          type: 'success',
          title: 'Collaborative filtering',
          detail: 'You have enough logging history — recommendations come from users with similar eating/exercise patterns.',
        }
      }
      if (strategy.value === 'cb') {
        return {
          type: 'info',
          title: 'Content-based (cold-start fallback)',
          detail: 'Not enough history yet — recommendations match your goal profile. Log 5+ meals (or 3+ workouts) to unlock collaborative filtering.',
        }
      }
      return null
    })

    const load = async () => {
      loading.value = true
      try {
        const { data } = await getRecommendations(recType.value, 5)
        items.value = data.items
        strategy.value = data.strategy
        loadHistory()
      } finally {
        loading.value = false
      }
    }

    const loadHistory = async () => {
      const { data } = await getRecommendationHistory(recType.value)
      history.value = data.items
    }

    onMounted(() => {
      load()
      loadHistory()
    })

    return { recType, items, history, strategy, strategyInfo, loading, userWeight, load }
  },
}
</script>

<style scoped>
.rec-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.strategy-banner {
  margin-bottom: 14px;
}

.rec-grid {
  display: grid;
  /* min(320px, 100%) keeps the grid at 1 column on narrow phones. */
  grid-template-columns: repeat(auto-fill, minmax(min(320px, 100%), 1fr));
  gap: 14px;
}

.rec-card {
  display: flex;
  gap: 12px;
  border: 1px solid #eef2f6;
  border-radius: 12px;
  padding: 14px 16px;
  background: #fbfdfe;
  transition: box-shadow 0.15s;
}

.rec-card:hover {
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}

.rec-rank {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #e6fffb;
  color: #0d9488;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-body {
  flex: 1;
}

.rec-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.rec-name {
  font-weight: 600;
  font-size: 15px;
  color: #0f172a;
}

.rec-reason {
  font-size: 12.5px;
  color: #475569;
  line-height: 1.5;
  margin-bottom: 8px;
}

.rec-nutrition {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #0d9488;
  font-weight: 500;
}
</style>
