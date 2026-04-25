<template>
  <div>
    <h1 class="page-title">📊 数据统计</h1>

    <div v-if="loading" class="loading">加载中...</div>

    <template v-else>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ data.note_count }}</div>
            <div class="stat-label">笔记总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📁</div>
          <div class="stat-info">
            <div class="stat-value">{{ data.category_count }}</div>
            <div class="stat-label">分类数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏷️</div>
          <div class="stat-info">
            <div class="stat-value">{{ data.tag_count }}</div>
            <div class="stat-label">标签数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-info">
            <div class="stat-value">{{ data.starred_count }}</div>
            <div class="stat-label">已收藏</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🗑️</div>
          <div class="stat-info">
            <div class="stat-value">{{ data.trashed_count }}</div>
            <div class="stat-label">回收站</div>
          </div>
        </div>
      </div>

      <div class="charts-row">
        <div class="card chart-card">
          <h3 class="chart-title">最近 7 天笔记创建趋势</h3>
          <div ref="trendChart" class="chart-container"></div>
        </div>
        <div class="card chart-card">
          <h3 class="chart-title">笔记类型分布</h3>
          <div ref="pieChart" class="chart-container"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, inject } from 'vue'
import { statsApi } from '../api'
import * as echarts from 'echarts'

const sourceTypeNames = {
  life: '生活', thought: '感想', knowledge: '知识',
  todo: '待办', idea: '灵感', work: '工作',
}

const sourceTypeColors = {
  life: '#10b981', thought: '#f59e0b', knowledge: '#3b82f6',
  todo: '#f43f5e', idea: '#8b5cf6', work: '#f97316',
  '未分类': '#94a3b8',
}

export default {
  name: 'StatsView',
  setup() {
    const toast = inject('toast')
    const loading = ref(true)
    const data = ref({
      note_count: 0, category_count: 0, tag_count: 0,
      starred_count: 0, trashed_count: 0,
      source_distribution: [], daily_counts: [],
    })
    const trendChart = ref(null)
    const pieChart = ref(null)
    let trendInstance = null
    let pieInstance = null

    const loadData = async () => {
      loading.value = true
      try {
        const res = await statsApi.overview()
        data.value = res.data
        loading.value = false
        await nextTick()
        renderCharts()
      } catch (e) {
        loading.value = false
        toast('加载统计数据失败', 'error')
      }
    }

    const renderCharts = () => {
      renderTrend()
      renderPie()
    }

    const renderTrend = () => {
      if (!trendChart.value) return
      if (trendInstance) trendInstance.dispose()
      trendInstance = echarts.init(trendChart.value)

      const daily = data.value.daily_counts || []
      const dates = daily.map(d => d.date.slice(5))
      const counts = daily.map(d => d.count)

      trendInstance.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#94a3b8' } },
          axisLabel: { color: '#64748b', fontSize: 12 },
        },
        yAxis: {
          type: 'value',
          minInterval: 1,
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 12 },
        },
        series: [{
          type: 'line',
          data: counts,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { color: '#3b82f6', width: 3 },
          itemStyle: { color: '#3b82f6' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59,130,246,0.3)' },
              { offset: 1, color: 'rgba(59,130,246,0.02)' },
            ]),
          },
        }],
      })
    }

    const renderPie = () => {
      if (!pieChart.value) return
      if (pieInstance) pieInstance.dispose()
      pieInstance = echarts.init(pieChart.value)

      const dist = data.value.source_distribution || []
      const pieData = dist.map(d => ({
        name: sourceTypeNames[d.type] || d.type,
        value: d.count,
        itemStyle: { color: sourceTypeColors[d.type] || '#94a3b8' },
      }))

      pieInstance.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '55%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, fontSize: 12, color: '#475569' },
          data: pieData,
        }],
      })
    }

    const handleResize = () => {
      if (trendInstance) trendInstance.resize()
      if (pieInstance) pieInstance.resize()
    }

    onMounted(() => {
      loadData()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      if (trendInstance) trendInstance.dispose()
      if (pieInstance) pieInstance.dispose()
    })

    return { loading, data, trendChart, pieChart }
  },
}
</script>
