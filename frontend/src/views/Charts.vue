<template>
  <div>
    <h1 class="page-title">Health Trends</h1>
    <p class="page-subtitle">Daily, weekly and monthly visualizations of your logs.</p>

    <!-- Filter row -->
    <div class="filter-row">
      <el-radio-group v-model="rangeDays" @change="reloadTrends">
        <el-radio-button :value="7">Last week</el-radio-button>
        <el-radio-button :value="30">Last month</el-radio-button>
        <el-radio-button :value="90">Last 3 months</el-radio-button>
        <el-radio-button :value="180">Last 6 months</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Calories in vs burned -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <template #header>
        <div class="card-header">
          <b>Calories: intake vs burned</b>
          <span class="muted">{{ rangeLabel }}</span>
        </div>
      </template>
      <div ref="lineEl" class="chart"></div>
    </el-card>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <!-- Net calories -->
      <el-col :xs="24" :lg="14" class="stack-col">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <b>Net calories per day</b>
              <span class="net-caption">
                <span class="swatch" :style="{ background: C.teal }"></span> deficit
                <span class="swatch" :style="{ background: C.orange }"></span> surplus
              </span>
            </div>
          </template>
          <div ref="netEl" class="chart"></div>
        </el-card>
      </el-col>
      <!-- Macros -->
      <el-col :xs="24" :lg="10" class="stack-col">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <b>Today's macros</b>
              <span class="muted" v-if="daily">
                {{ Math.round(daily.calories_in) }} kcal
              </span>
            </div>
          </template>
          <div ref="macroEl" class="chart chart-donut"></div>
          <div class="donut-legend">
            <span><span class="swatch" :style="{ background: C.teal }"></span>
              Protein {{ macroVal('protein') }}g</span>
            <span><span class="swatch" :style="{ background: C.yellow }"></span>
              Carbs {{ macroVal('carbs') }}g</span>
            <span><span class="swatch" :style="{ background: C.violet }"></span>
              Fat {{ macroVal('fat') }}g</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Monthly -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <template #header>
        <div class="card-header">
          <b>Monthly totals</b>
          <span class="muted">Last {{ monthly.length }} months</span>
        </div>
      </template>
      <div ref="monthEl" class="chart"></div>
    </el-card>

    <!-- Table view (accessibility: the same data as the charts) -->
    <el-card shadow="never">
      <template #header><b>Data table</b></template>
      <el-table :data="tableRows" size="small" max-height="360">
        <el-table-column prop="date" label="Date" width="120" />
        <el-table-column prop="calories_in" label="Calories in (kcal)" width="150" />
        <el-table-column prop="calories_out" label="Burned (kcal)" width="130" />
        <el-table-column label="Net (kcal)" width="110">
          <template #default="{ row }">
            {{ row.net > 0 ? '+' : '' }}{{ row.net }}
          </template>
        </el-table-column>
        <el-table-column prop="protein" label="Protein (g)" />
        <el-table-column prop="carbs" label="Carbs (g)" />
        <el-table-column prop="fat" label="Fat (g)" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { useStore } from 'vuex'
import { getDailyStats, getTrends, getMonthly } from '@/api/stats'

// Chart palette (dataviz skill, validator-checked). Same entities in both
// themes - light and dark are separate steps of the same ramps, each
// validated against its own surface:
//   light: teal #14b8a6, orange #eb6834, yellow #eda100, violet #4a3aa7
//   dark:  teal #0e9f92, orange #e96830, yellow #b8860b, violet #6a57c4
//   (orange/yellow never share a chart, so they never need to separate.)
const LIGHT = {
  ink: '#52514e', muted: '#898781', grid: '#e1e0d9', axis: '#c3c2b7',
  surface: '#fcfcfb', tooltip: '#fff', tooltipBorder: '#e1e0d9',
  teal: '#14b8a6', orange: '#eb6834', yellow: '#eda100', violet: '#4a3aa7',
  tealArea: 'rgba(20, 184, 166, 0.08)',
}
const DARK = {
  ink: '#d5dbe3', muted: '#8b95a5', grid: '#2a2b2d', axis: '#3c3d3f',
  surface: '#1d1e1f', tooltip: '#1d1e1f', tooltipBorder: '#303133',
  teal: '#0e9f92', orange: '#e96830', yellow: '#b8860b', violet: '#6a57c4',
  tealArea: 'rgba(14, 159, 146, 0.16)',
}

export default {
  name: 'ChartsView',
  setup() {
    const store = useStore()
    const isDark = computed(() => store.getters['ui/isDark'])
    const C = computed(() => (isDark.value ? DARK : LIGHT))

    const lineEl = ref(null)
    const netEl = ref(null)
    const macroEl = ref(null)
    const monthEl = ref(null)
    const rangeDays = ref(30)
    const series = ref([])
    const monthly = ref([])
    const daily = ref(null)
    let charts = []

    const rangeLabel = computed(() => `Daily · last ${rangeDays.value} days`)

    const tableRows = computed(() =>
      series.value.map((d) => ({
        date: d.date,
        calories_in: d.calories_in,
        calories_out: d.calories_out,
        net: d.net,
        protein: d.macros.protein,
        carbs: d.macros.carbs,
        fat: d.macros.fat,
      }))
    )

    const macroVal = (key) =>
      daily.value ? Math.round(daily.value.macros[key]) : 0

    const baseGrid = () => ({
      left: 8, right: 16, top: 12, bottom: 8, containLabel: true,
    })
    const baseXAxis = () => ({
      type: 'category',
      boundaryGap: true,
      axisLine: { lineStyle: { color: C.value.axis } },
      axisTick: { show: false },
      axisLabel: { color: C.value.muted, fontSize: 11 },
    })
    const baseYAxis = () => ({
      type: 'value',
      splitLine: { lineStyle: { color: C.value.grid } },
      axisLabel: { color: C.value.muted, fontSize: 11 },
    })

    const makeLineOption = () => ({
      grid: baseGrid(),
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross', lineStyle: { color: C.value.muted } },
        backgroundColor: C.value.tooltip,
        borderColor: C.value.tooltipBorder,
        textStyle: { color: C.value.ink, fontSize: 12 },
      },
      legend: {
        top: 0, right: 0, itemWidth: 14, itemHeight: 8,
        textStyle: { color: C.value.muted, fontSize: 12 },
      },
      xAxis: { ...baseXAxis(), data: series.value.map((d) => d.date.slice(5)) },
      yAxis: baseYAxis(),
      series: [
        {
          name: 'Calories in',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: C.value.teal },
          itemStyle: { color: C.value.teal, borderColor: C.value.surface, borderWidth: 2 },
          areaStyle: { color: C.value.tealArea },
          data: series.value.map((d) => d.calories_in),
        },
        {
          name: 'Burned',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: C.value.orange },
          itemStyle: { color: C.value.orange, borderColor: C.value.surface, borderWidth: 2 },
          data: series.value.map((d) => d.calories_out),
        },
      ],
    })

    const makeNetOption = () => ({
      grid: baseGrid(),
      tooltip: {
        trigger: 'item',
        backgroundColor: C.value.tooltip,
        borderColor: C.value.tooltipBorder,
        textStyle: { color: C.value.ink, fontSize: 12 },
        formatter: (p) =>
          `${p.name}<br/>Net: ${p.value > 0 ? '+' : ''}${p.value} kcal`,
      },
      xAxis: { ...baseXAxis(), data: series.value.map((d) => d.date.slice(5)) },
      yAxis: baseYAxis(),
      series: [
        {
          name: 'Net kcal',
          type: 'bar',
          barWidth: '55%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: (p) => (p.value >= 0 ? C.value.orange : C.value.teal),
          },
          data: series.value.map((d) => d.net),
        },
      ],
    })

    const makeMacroOption = () => ({
      tooltip: {
        trigger: 'item',
        backgroundColor: C.value.tooltip,
        borderColor: C.value.tooltipBorder,
        textStyle: { color: C.value.ink, fontSize: 12 },
        formatter: '{b}: {c}g ({d}%)',
      },
      legend: { show: false },
      series: [
        {
          name: 'Macros',
          type: 'pie',
          radius: ['52%', '74%'],
          center: ['50%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderColor: C.value.surface, // 2px surface gaps between segments
            borderWidth: 2,
            borderRadius: 4,
          },
          label: { show: false },
          data: [
            { name: 'Protein', value: macroVal('protein'), itemStyle: { color: C.value.teal } },
            { name: 'Carbs', value: macroVal('carbs'), itemStyle: { color: C.value.yellow } },
            { name: 'Fat', value: macroVal('fat'), itemStyle: { color: C.value.violet } },
          ],
        },
      ],
    })

    const makeMonthlyOption = () => ({
      grid: baseGrid(),
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: C.value.tooltip,
        borderColor: C.value.tooltipBorder,
        textStyle: { color: C.value.ink, fontSize: 12 },
      },
      legend: {
        top: 0, right: 0, itemWidth: 14, itemHeight: 8,
        textStyle: { color: C.value.muted, fontSize: 12 },
      },
      xAxis: { ...baseXAxis(), data: monthly.value.map((m) => m.month) },
      yAxis: baseYAxis(),
      series: [
        {
          name: 'Calories in',
          type: 'bar',
          barWidth: '28%',
          itemStyle: { color: C.value.teal, borderRadius: [3, 3, 0, 0] },
          data: monthly.value.map((m) => m.calories_in),
        },
        {
          name: 'Burned',
          type: 'bar',
          barWidth: '28%',
          itemStyle: { color: C.value.orange, borderRadius: [3, 3, 0, 0] },
          data: monthly.value.map((m) => m.calories_out),
        },
      ],
    })

    const renderAll = () => {
      if (lineEl.value) renderChart(lineEl.value, makeLineOption())
      if (netEl.value) renderChart(netEl.value, makeNetOption())
      if (macroEl.value) renderChart(macroEl.value, makeMacroOption())
      if (monthEl.value) renderChart(monthEl.value, makeMonthlyOption())
    }

    const renderChart = (el, option) => {
      const chart = echarts.getInstanceByDom(el) || echarts.init(el)
      chart.setOption(option, { notMerge: true })
      if (!charts.includes(chart)) charts.push(chart)
    }

    const reloadTrends = async () => {
      const { data } = await getTrends(rangeDays.value)
      series.value = data.series
      renderAll()
    }

    const loadMonthly = async () => {
      const { data } = await getMonthly(6)
      monthly.value = data.series
      renderAll()
    }

    const loadDaily = async () => {
      const { data } = await getDailyStats()
      daily.value = data
      renderAll()
    }

    const onResize = () => charts.forEach((c) => c.resize())

    watch(rangeDays, reloadTrends)
    // Re-render with the other theme's validated palette when it flips.
    watch(isDark, renderAll)
    onMounted(async () => {
      await Promise.all([reloadTrends(), loadMonthly(), loadDaily()])
      window.addEventListener('resize', onResize)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('resize', onResize)
      charts.forEach((c) => c.dispose())
      charts = []
    })

    return {
      lineEl, netEl, macroEl, monthEl, rangeDays, series, monthly, daily,
      rangeLabel, tableRows, macroVal, reloadTrends, C,
    }
  },
}
</script>

<style scoped>
.filter-row {
  margin-bottom: 14px;
}

.chart {
  height: 300px;
  width: 100%;
}

.chart-donut {
  height: 200px;
}

.net-caption,
.donut-legend {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 12.5px;
  color: #64748b;
}

.swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  margin-right: 5px;
}

.donut-legend {
  justify-content: center;
}

@media (max-width: 991px) {
  .stack-col {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .chart {
    height: 220px;
  }

  .chart-donut {
    height: 180px;
  }

  .net-caption,
  .donut-legend {
    gap: 10px;
    flex-wrap: wrap;
  }
}
</style>
