<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { getReceipts, receipts } from '../../firebase/fireStore.svelte';
  import { standardCategories } from './utils/categoryMapping';
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
  import { Separator } from './components/ui/separator';
  import { Button } from './components/ui/button';
  import ChartDataLabels from 'chartjs-plugin-datalabels';

  // Register Chart.js components
  Chart.register(...registerables, ChartDataLabels);

  // State variables
  let chartElement: HTMLCanvasElement;
  let pieChart: Chart | null = null;
  let isLoading = true;

  // Properly type chartData for Chart.js
  let chartData = {
    labels: [] as string[],
    datasets: [
      {
        data: [] as number[],
        backgroundColor: [] as string[],
        hoverOffset: 4
      }
    ]
  };

  // Function to prepare data
  async function generateChart() {
    try {
      // Get receipts data
      await getReceipts();
      isLoading = false;

      if (receipts.length === 0) return;

      // Create totals by category
      const categoryTotals: Record<string, number> = {};

      // Initialize categories with 0
      standardCategories.forEach((category) => {
        categoryTotals[category] = 0;
      });

      // Sum up totals by category - use regular for loop to avoid reactive state issues
      for (let i = 0; i < receipts.length; i++) {
        const receipt = receipts[i];
        const category = receipt.category || 'Other';
        const total = parseFloat(String(receipt.total || '0'));

        if (!isNaN(total)) {
          categoryTotals[category] = (categoryTotals[category] || 0) + total;
        }
      }

      // Filter out categories with 0 total
      const filteredCategories = Object.keys(categoryTotals).filter(
        (category) => categoryTotals[category] > 0
      );

      const totals = filteredCategories.map((category) => categoryTotals[category]);

      // Chart colors for categories
      const colors = [
        '#f00a15', // red
        '#0a38f0', // blue
        '#d5f00a', // yellow
        '#0af0dd', // teal
        '#9966FF', // purple
        '#FF9F40', // orange
        '#34f00a', // lime
        '#2C5F2D', // dark green
        '#EF476F', // pink
        '#0af0a7', // blue/green
        '#f00ae8' // pinkish purple
      ];

      // Update chart data
      chartData.labels = filteredCategories;
      chartData.datasets[0].data = totals;
      chartData.datasets[0].backgroundColor = colors.slice(0, filteredCategories.length);

      // Wait for next tick to ensure DOM is ready
      setTimeout(() => {
        createOrUpdateChart();
      }, 0);
    } catch (error) {
      console.error('Error preparing chart data:', error);
    }
  }

  // Function to create or update the chart
  function createOrUpdateChart() {
    if (!chartElement) return;

    // Check if canvas is already in use - destroy previous instance
    if (pieChart) {
      pieChart.destroy();
      pieChart = null;
    }

    // Create a new chart
    pieChart = new Chart(chartElement, {
      type: 'pie',
      data: chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            padding: 15,
            titleFont: {
              size: 16
            },
            bodyFont: {
              size: 16
            },
            callbacks: {
              label: function (context) {
                const value = context.raw as number;
                const total = context.dataset.data.reduce(
                  (sum: number, val: number) => sum + val,
                  0
                );
                const percentage = ((value / total) * 100).toFixed(1);
                return `${context.label}: $${value.toFixed(2)} (${percentage}%)`;
              }
            }
          },
          legend: {
            position: 'right',
            labels: {
              color: '#fff',
              font: {
                size: 16
              },
              usePointStyle: true,
              pointStyle: 'rectRounded'
            }
          },
          datalabels: {
            formatter: (value: number, ctx) => {
              const sum = ctx.chart.data.datasets[0].data.reduce(
                (a: number, b: any) => a + (typeof b === 'number' ? b : 0),
                0
              );

              if (sum <= 0) return '';
              const percentage = ((value / sum) * 100).toFixed(1) + '%';
              return percentage;
            },
            color: '#fff',
            font: {
              weight: 'bold',
              size: 16
            },
            textStrokeColor: '#000',
            textStrokeWidth: 1,
            textShadowBlur: 3,
            textShadowColor: 'rgba(0,0,0,0.5)'
          }
        }
      }
    });
  }

  // Calculate total spending across all categories
  function calculateTotalSpending() {
    if (!chartData.datasets[0].data.length) return 0;

    return chartData.datasets[0].data.reduce((total, amount) => total + amount, 0);
  }

  onMount(() => {
    generateChart();
  });
</script>

<main>
  <!-- TODO: Main container - minimal padding, needs redesign -->
  <div class="mx-auto">
    <!-- TODO: Page Header Section - needs proper styling -->
    <div class="flex flex-col items-center justify-between gap-4 md:flex-row">
      <div class="flex flex-col">
        <h1 class="text-center text-3xl font-bold sm:text-start">Spending Analysis</h1>
        <p class="mb-2 text-muted-foreground">Track your spending patterns</p>
      </div>

      <Button variant="outline" on:click={generateChart}>Refresh Data</Button>
    </div>

    <Separator />

    <!-- TODO: Chart Section - should be in its own full row -->
    <div class="grid w-full">
      <Card class="col-span-full p-5 duration-500 animate-in fade-in">
        <CardHeader>
          <div class="flex justify-between">
            <CardTitle class="text-2xl">Spending by Category</CardTitle>
          </div>
          <CardDescription>
            Breakdown of your expenditures across different categories
          </CardDescription>
        </CardHeader>

        <CardContent class="p-5">
          {#if isLoading}
            <div class="flex h-80 items-center justify-center">
              <p class="text-muted-foreground">Loading chart data...</p>
            </div>
          {:else if receipts.length === 0}
            <div class="flex h-80 items-center justify-center">
              <p class="text-muted-foreground">
                No receipt data found. Please add some receipts first.
              </p>
            </div>
          {:else}
            <!-- Removed padding and margins from chart container -->
            <div class="h-[600px] w-full">
              <canvas bind:this={chartElement}></canvas>
            </div>
          {/if}
        </CardContent>
      </Card>
    </div>

    <!-- TODO: Summary Cards Section - should be in a separate row -->
    <div class="mt-6 grid gap-6 md:grid-cols-2">
      {#if !isLoading && receipts.length > 0}
        <Card class="duration-500 animate-in fade-in">
          <CardHeader>
            <CardTitle class="text-xl">Total Spending</CardTitle>
            <CardDescription>Your total expenditure across all categories</CardDescription>
          </CardHeader>

          <CardContent>
            <p class="text-4xl font-bold">${calculateTotalSpending().toFixed(2)}</p>
          </CardContent>
        </Card>

        <Card class="duration-500 animate-in fade-in">
          <CardHeader>
            <CardTitle class="text-xl">Categories</CardTitle>
            <CardDescription>Number of spending categories</CardDescription>
          </CardHeader>

          <CardContent>
            <p class="text-4xl font-bold">{chartData.labels.length}</p>
          </CardContent>
        </Card>
      {/if}
    </div>

    <!-- TODO: Category Breakdown Table Section - detailed view of spending -->
    <div class="mt-6">
      {#if !isLoading && receipts.length > 0 && chartData.labels.length > 0}
        <Card class="duration-500 animate-in fade-in">
          <CardHeader>
            <CardTitle class="text-xl">Category Breakdown</CardTitle>
            <CardDescription>Detailed spending breakdown by category</CardDescription>
          </CardHeader>

          <CardContent>
            <div class="rounded-md border">
              <table class="w-full">
                <thead>
                  <tr class="border-b transition-colors hover:bg-muted/50">
                    <th class="p-4 text-left font-medium">Category</th>
                    <th class="p-4 text-right font-medium">Amount</th>
                    <th class="p-4 text-right font-medium">Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {#each chartData.labels as label, i}
                    <tr class="border-b transition-colors hover:bg-muted/50">
                      <td class="p-4 align-middle font-medium">
                        <div class="flex items-center gap-2">
                          <div
                            class="h-4 w-4 rounded"
                            style="background-color: {chartData.datasets[0].backgroundColor[i]};"
                          ></div>
                          {label}
                        </div>
                      </td>
                      <td class="p-4 text-right align-middle"
                        >${chartData.datasets[0].data[i].toFixed(2)}</td
                      >
                      <td class="p-4 text-right align-middle">
                        {((chartData.datasets[0].data[i] / calculateTotalSpending()) * 100).toFixed(
                          1
                        )}%
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      {/if}
    </div>
  </div>
</main>

<style>
  /* Apply transitions to cards for hover effects */
  :global(.card) {
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
  }

  :global(.card:hover) {
    transform: translateY(-2px);
    box-shadow:
      0 10px 25px -5px rgba(0, 0, 0, 0.1),
      0 8px 10px -6px rgba(0, 0, 0, 0.1);
  }
</style>
