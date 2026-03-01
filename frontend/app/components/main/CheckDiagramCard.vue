<template>
  <n-card class="data-card" title="Check diagram" :bordered="false">
    <div class="chart-placeholder">
      <v-chart v-if="!isLoadingStats" class="echarts-instance" :option="chartOption" autoresize />
      <n-spin v-else size="medium" />
    </div>
  </n-card>
</template>

<script setup lang="ts">
  import { use } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart } from 'echarts/charts';
  import { GridComponent, TooltipComponent } from 'echarts/components';
  import VChart from 'vue-echarts';

  use([CanvasRenderer, LineChart, GridComponent, TooltipComponent]);

  const { data: stats, isLoading: isLoadingStats } = useSnapshotStatsQuery();

  const chartOption = computed(() => {
    const sourceData = stats.value || [];

    const xAxisData = sourceData.map((item: any) => item.date);
    const seriesData = sourceData.map((item: any) => item.count);

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: MEDIUM,
        borderColor: LIGHT,
        textStyle: { color: WHITE_SECONDARY },
      },
      grid: {
        left: '0%',
        right: '0%',
        top: '10px',
        bottom: '0%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: xAxisData,
        boundaryGap: false,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: GRAY,
          formatter: (value: string) => {
            const date = new Date(value);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
      yAxis: {
        type: 'value',
        splitLine: {
          lineStyle: { color: LIGHT },
        },
        axisLabel: { color: GRAY },
      },
      series: [
        {
          data: seriesData,
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            color: ACCENT,
            width: 3,
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: ACCENT_DARK },
                { offset: 1, color: DARK },
              ],
            },
          },
        },
      ],
    };
  });
</script>

<style scoped lang="scss">
  .data-card {
    background-color: $medium;
    border-radius: 12px;
  }

  .chart-placeholder {
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

  .echarts-instance {
    width: 100%;
    height: 100%;
  }
</style>
