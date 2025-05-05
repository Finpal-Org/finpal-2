<script lang="ts">
  import { getReceipts } from '../../firebase/fireStore.svelte';
  import { Button } from './components/ui/button/index';
  import { analyzeReceipt } from './services/receiptService';
  import { isHeicFile, convertHeicToJpeg } from './components/utils/heicValidator';

  // Status vars
  let isProcessing = false;
  let statusMsg = '';
  let error = '';
  let fileInput: any;

  /**
   * Handle file upload & conversion
   */
  async function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = target.files;

    // Reset status
    error = '';
    statusMsg = '';

    if (!files?.length) {
      error = 'No file selected';
      return;
    }

    const file = files[0];

    // Check size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      error = 'File size exceeds 5MB limit';
      return;
    }

    isProcessing = true;

    try {
      let fileToProcess = file;

      // Convert HEIC if needed
      if (await isHeicFile(file)) {
        statusMsg = 'Converting HEIC...';
        fileToProcess = await convertHeicToJpeg(file);
      }

      // Process file
      statusMsg = 'Processing receipt...';
      await analyzeReceipt(fileToProcess);

      // Success
      statusMsg = 'Receipt processed successfully!';

      // Reset input
      if (fileInput) fileInput.value = '';

      // Refresh receipts
      await getReceipts();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Processing error';
      console.error('Receipt error:', err);
    } finally {
      isProcessing = false;
    }
  }
</script>

<div class="">
  <div class="upload-container flex flex-col items-center justify-center gap-2">
    <Button size="lg" class="flex gap-2 p-8" on:click={() => !isProcessing && fileInput.click()}>
      {#if isProcessing}
        <span class="loading">Processing...</span>
      {:else}
        <span class="upload-icon">➕</span>
        <span>Upload Receipt</span>
      {/if}
    </Button>

    <input
      id="receipt-upload"
      type="file"
      accept="image/jpeg,image/png,image/tiff,application/pdf,image/heic,image/heif"
      bind:this={fileInput}
      on:change={handleFileUpload}
      disabled={isProcessing}
      class="hidden"
    />
  </div>

  {#if statusMsg}
    <div class="status-message">{statusMsg}</div>
  {/if}

  {#if error}
    <div class="error-message">{error}</div>
  {/if}
</div>

<style></style>
