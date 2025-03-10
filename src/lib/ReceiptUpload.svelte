<script lang="ts">
  import { getReceipts } from '../../firebase/fireStore.svelte';
  import { Button } from './components/ui/button/index';
  import { Input } from './components/ui/input/index';
  import { Label } from './components/ui/label/index';
  import { analyzeReceipt } from './services/receiptService';

  // Upload status
  let isProcessing = false;
  let uploadStatus = '';
  let error = '';
  let uploadComplete = false;
  let uploadSuccess = false;

  // File input reference
  let fileInput: any;

  /**
   * Handles file upload when a user selects a file, svelte dont require (event args in input element)
   */
  async function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    const files = target.files;

    // Reset status
    error = '';
    uploadStatus = '';
    uploadComplete = false;
    uploadSuccess = false;

    if (!files || files.length === 0) {
      error = 'No file selected';
      return;
    }

    const file = files[0];

    // Basic validation
    if (file.size > 4 * 1024 * 1024) {
      error = 'File size exceeds 4MB limit';
      return;
    }

    isProcessing = true;
    uploadStatus = 'Uploading and analyzing receipt...';

    try {
      // Send to receipt service for processing
      await analyzeReceipt(file);

      // Success status update
      uploadComplete = true;
      uploadSuccess = true;
      uploadStatus = 'Receipt uploaded and processed successfully!';

      // Reset file input
      if (fileInput) {
        fileInput.value = '';
      }
      await getReceipts(); //refresh receipts after upload (await for fetching)
    } catch (err) {
      // Error handling
      uploadComplete = true;
      uploadSuccess = false;
      error = err instanceof Error ? err.message : 'An error occurred during processing';
      console.error('Receipt processing error:', err);
    } finally {
      // end of proccessing..
      isProcessing = false;
    }
  }
</script>

<div class="">
  <div class="upload-container flex flex-col items-center justify-center gap-2">
    <!-- TODO: make button show 3 options: 1- upload 2- capture 3-email forwarding -->
    <Button
      size="lg"
      class="flex gap-2 p-8"
      on:click={() => {
        // if not proccessing a receipt -> click for file input
        if (!isProcessing) fileInput.click();
      }}
    >
      {#if isProcessing}
        <span class="loading">Processing...</span>
      {:else}
        <!-- TODO: svg icon for + sign -->
        <span class="upload-icon">➕</span>
        <span>Upload Receipt</span>
      {/if}
    </Button>

    <!-- this input element is referenced (bind) by fileinput variable -->
    <input
      id="receipt-upload"
      type="file"
      accept="image/jpeg,image/png,image/tiff,application/pdf"
      bind:this={fileInput}
      on:change={handleFileUpload}
      disabled={isProcessing}
      class="hidden"
    />
  </div>

  {#if uploadStatus}
    <div class="status-message" class:success={uploadSuccess}>
      {uploadStatus}
    </div>
  {/if}

  {#if error}
    <div class="error-message">
      {error}
    </div>
  {/if}
</div>

<style></style>
