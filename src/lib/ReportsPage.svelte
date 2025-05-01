<script lang="ts">
  // Import shadcn components
  import { Button } from './components/ui/button';
  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
  } from './components/ui/card';
  import { Separator } from './components/ui/separator';
  import { getReceipts, receipts } from '../../firebase/fireStore.svelte';
  import { onMount } from 'svelte';
  import { exportReceiptsToExcel, exportReceiptsByCategory } from './services/excelService';
  import { categoryMapping, standardCategories } from './utils/categoryMapping';

  // Group by select component - using individual imports
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
  } from './components/ui/select';

  // State management
  let isLoading = $state(false);
  let isExporting = $state(false);
  let exportSuccess = $state(false);
  let exportError = $state<string | null>(null);
  let exportType = $state<'all' | 'category'>('all');
  let exportFileName = $state('receipts-export.xlsx');
  let selectedCategory = $state<string | null>(null);

  // Statistics state
  let totalReceipts = $derived(receipts.length);

  // Helper function to get merchant name from either structure
  function getMerchantName(receipt: any): string {
    return receipt?.vendor?.name || receipt?.merchantName || 'Unknown';
  }

  // Helper function to get address from either structure
  function getAddress(receipt: any): string {
    return receipt?.vendor?.address || receipt?.address || '';
  }

  // Helper function to get phone from either structure
  function getPhone(receipt: any): string {
    return receipt?.vendor?.phone || receipt?.phone || '';
  }

  // Helper function to get tax from either structure
  function getTax(receipt: any): string {
    return receipt?.tax || receipt?.totalTax || '';
  }

  // Helper function to get total from either structure
  function getTotal(receipt: any): string {
    return receipt?.total || '0.00';
  }

  // Helper function to get date from either structure
  function getDate(receipt: any): string {
    return receipt?.date || 'Unknown';
  }

  // Standardize category values using categoryMapping
  let categories = $derived(
    receipts.reduce(
      (acc, receipt) => {
        // Map the receipt category to a standard category or use 'Other'
        const rawCategory = receipt.category || 'Other';
        const standardCategory = categoryMapping[rawCategory] || rawCategory;

        acc[standardCategory] = (acc[standardCategory] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>
    )
  );

  let totalAmount = $derived(
    receipts.reduce((sum, receipt) => {
      const total = getTotal(receipt) ? parseFloat(getTotal(receipt).toString()) : 0;
      return sum + (isNaN(total) ? 0 : total);
    }, 0)
  );

  // Map category for comparison to ensure consistent lookup
  let filteredReceipts = $derived(
    selectedCategory
      ? receipts.filter((receipt) => {
          const rawCategory = receipt.category || 'Other';
          const standardCategory = categoryMapping[rawCategory] || rawCategory;
          return standardCategory === selectedCategory;
        })
      : receipts
  );

  // Unique categories for dropdown - use standardCategories as a base and add any additional
  // categories that might exist in the receipts but not in the standard list
  let uniqueCategories = $derived(
    // Start with categories from receipts
    [...new Set([...standardCategories, ...Object.keys(categories)])].sort()
  );

  // Load receipts on mount
  onMount(async () => {
    try {
      isLoading = true;
      await getReceipts();
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  });

  // Export handlers
  async function handleExport() {
    try {
      isExporting = true;
      exportSuccess = false;
      exportError = null;

      if (receipts.length === 0) {
        exportError = 'No receipts found to export';
        return;
      }

      const receiptsToExport = selectedCategory ? filteredReceipts : receipts;

      if (receiptsToExport.length === 0) {
        exportError = 'No receipts found for the selected category';
        return;
      }

      // Create a custom filename that includes the category name if a category is selected
      let fileName = exportFileName;
      if (selectedCategory) {
        const baseName = fileName.replace('.xlsx', '');
        fileName = `${baseName}-${selectedCategory.toLowerCase()}.xlsx`;
      }

      // Always export to a single sheet, regardless of export type
      await exportReceiptsToExcel(receiptsToExport, fileName);

      exportSuccess = true;
    } catch (err) {
      console.error('Export error:', err);
      exportError = 'Failed to export receipts';
    } finally {
      isExporting = false;

      // Reset success message after a delay
      if (exportSuccess) {
        setTimeout(() => {
          exportSuccess = false;
        }, 3000);
      }
    }
  }

  // Handle filename change
  function handleFileNameChange(e: Event) {
    const target = e.target as HTMLInputElement;
    exportFileName = target.value;

    // Add .xlsx extension if not present
    if (!exportFileName.toLowerCase().endsWith('.xlsx')) {
      exportFileName += '.xlsx';
    }
  }

  // Reset category filter
  function resetCategoryFilter() {
    selectedCategory = null;
  }

  // Check if export is disabled
  function isExportDisabled(): boolean {
    return (
      isExporting ||
      receipts.length === 0 ||
      (selectedCategory !== null && filteredReceipts.length === 0)
    );
  }

  // Helper function to get standardized category for display
  function getStandardCategory(category: string | undefined): string {
    const rawCategory = category || 'Other';
    return categoryMapping[rawCategory] || rawCategory;
  }
</script>

<main>
  <div class="mx-auto space-y-8 p-6">
    <div class="flex flex-col items-center justify-between gap-4 md:flex-row">
      <div class="flex flex-col">
        <h1 class="text-center text-3xl font-bold sm:text-start">Reports</h1>
        <p class="text-muted-foreground">Generate and export receipt reports</p>
      </div>
    </div>

    <div class="grid gap-6">
      <Separator />

      <!-- Category filter card -->
      <Card>
        <CardHeader>
          <CardTitle>Filter by Category</CardTitle>
          <CardDescription>Select a category to filter your receipts</CardDescription>
        </CardHeader>

        <CardContent>
          <div class="space-y-2">
            <div class="relative">
              <select
                id="category-filter"
                class="w-full rounded-md border border-input px-3 py-2"
                bind:value={selectedCategory}
              >
                <option value={null}>All Categories</option>
                {#each uniqueCategories as category}
                  <option value={category}>{category}</option>
                {/each}
              </select>
            </div>
            {#if selectedCategory}
              <div class="flex items-center justify-between">
                <p class="text-sm">
                  <span class="font-medium">{filteredReceipts.length}</span> receipts in category '{selectedCategory}'
                </p>
                <button on:click={resetCategoryFilter} class="text-sm text-primary hover:underline">
                  Reset Filter
                </button>
              </div>
            {/if}
          </div>
        </CardContent>
      </Card>

      <!-- Sample receipts table (preview of what will be exported) -->
      <Card>
        <CardHeader>
          <CardTitle>Receipt Data Preview</CardTitle>
          <CardDescription>
            {#if selectedCategory}
              Showing receipts for category: <span class="font-medium">{selectedCategory}</span>
            {:else}
              Preview of all receipts
            {/if}
          </CardDescription>
        </CardHeader>

        <CardContent>
          {#if isLoading}
            <div class="p-4 text-center">Loading receipts...</div>
          {:else if receipts.length === 0}
            <div class="p-4 text-center">No receipts found. Please upload a receipt first.</div>
          {:else if selectedCategory && filteredReceipts.length === 0}
            <div class="p-4 text-center">No receipts found for category: {selectedCategory}</div>
          {:else}
            <div class="overflow-x-auto">
              <table class="w-full border-collapse">
                <thead>
                  <tr class="border-b">
                    <th class="px-4 py-2 text-left">Merchant</th>
                    <th class="px-4 py-2 text-left">Category</th>
                    <th class="px-4 py-2 text-left">Date</th>
                    <th class="px-4 py-2 text-right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {#each (selectedCategory ? filteredReceipts : receipts).slice(0, 5) as receipt, i}
                    <tr class="border-b hover:bg-muted/50">
                      <td class="px-4 py-2">{getMerchantName(receipt)}</td>
                      <td class="px-4 py-2">{getStandardCategory(receipt.category)}</td>
                      <td class="px-4 py-2">{getDate(receipt)}</td>
                      <td class="px-4 py-2 text-right">{getTotal(receipt)}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>

              {#if selectedCategory ? filteredReceipts.length > 5 : receipts.length > 5}
                <div class="mt-2 text-center text-sm text-muted-foreground">
                  Showing 5 of {selectedCategory ? filteredReceipts.length : receipts.length} receipts.
                  Export to see all.
                </div>
              {/if}
            </div>
          {/if}
        </CardContent>
      </Card>
      <div class="grid gap-6 md:grid-cols-[1fr]">
        <!-- Export card -->
        <Card>
          <CardHeader>
            <CardTitle>Export Receipts</CardTitle>
            <CardDescription>
              {#if selectedCategory}
                Export receipts from category '{selectedCategory}'
              {:else}
                Export all receipts to Excel format
              {/if}
            </CardDescription>
          </CardHeader>

          <CardContent class="space-y-4">
            <!-- File Name Input -->
            <div class="space-y-2">
              <label for="file-name" class="text-sm font-medium">Save as File Name</label>
              <input
                id="file-name"
                type="text"
                class="w-full rounded-md border border-input px-3 py-2"
                value={exportFileName}
                on:change={handleFileNameChange}
              />
              {#if selectedCategory}
                <p class="text-xs text-muted-foreground">
                  Category name will be added to the file name automatically
                </p>
              {/if}
            </div>

            <!-- Export Button -->
            <Button on:click={handleExport} disabled={isExportDisabled()} class="w-full">
              {#if isExporting}
                <span class="mr-2 animate-spin">⏳</span> Exporting...
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  x="0px"
                  y="0px"
                  width="40"
                  height="40"
                  viewBox="0 0 48 48"
                  class="mr-2"
                >
                  <path
                    fill="#4CAF50"
                    d="M41,10H25v28h16c0.553,0,1-0.447,1-1V11C42,10.447,41.553,10,41,10z"
                  ></path><path
                    fill="#FFF"
                    d="M32 15H39V18H32zM32 25H39V28H32zM32 30H39V33H32zM32 20H39V23H32zM25 15H30V18H25zM25 25H30V28H25zM25 30H30V33H25zM25 20H30V23H25z"
                  ></path><path fill="#2E7D32" d="M27 42L6 38 6 10 27 6z"></path><path
                    fill="#FFF"
                    d="M19.129,31l-2.411-4.561c-0.092-0.171-0.186-0.483-0.284-0.938h-0.037c-0.046,0.215-0.154,0.541-0.324,0.979L13.652,31H9.895l4.462-7.001L10.274,17h3.837l2.001,4.196c0.156,0.331,0.296,0.725,0.42,1.179h0.04c0.078-0.271,0.224-0.68,0.439-1.22L19.237,17h3.515l-4.199,6.939l4.316,7.059h-3.74V31z"
                  ></path>
                </svg>
                Export to Excel
              {/if}
            </Button>

            <!-- Export Messages -->
            {#if exportSuccess}
              <div class="rounded bg-green-50 p-2 text-sm font-medium text-green-600">
                ✅ Export successful! File downloaded.
              </div>
            {/if}

            {#if exportError}
              <div class="rounded bg-red-50 p-2 text-sm font-medium text-red-600">
                ❌ {exportError}
              </div>
            {/if}
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</main>
