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
  import ReceiptUpload from './ReceiptUpload.svelte';
  import ReceiptEdit from './components/ReceiptEdit.svelte';
  import ReceiptDetails from './components/ReceiptDetails.svelte';
  import ReceiptCardContent from './components/ReceiptCardContent.svelte';

  // init loading to false
  let isLoading = $state(false);

  onMount(async () => {
    // on mount, wait to get receipts
    try {
      isLoading = true;
      await getReceipts();
    } catch (err) {
      console.error(err);
    } finally {
      isLoading = false;
    }
  });

  // Define interfaces for receipt data
  // export let receiptData = receiptDataJson;
</script>

<main>
  <div class=" mx-auto space-y-8 p-6">
    <div class="flex flex-col items-center justify-between gap-4 md:flex-row">
      <div class="flex flex-col">
        <h1 class="text-center text-3xl font-bold sm:text-start">Receipts</h1>
        <p class="text-muted-foreground">Manage your receipts</p>
      </div>
      <ReceiptUpload />
    </div>
    <div class="grid gap-6">
      <Separator />
      <!-- (auto-fit) stacks receipt in the row infinitly if there is space (350px each receipt) -->
      <div class="grid grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-10">
        <!-- Loading msgs -->
        {#if isLoading}
          <h1>Loading...</h1>
        {:else if receipts.length === 0}
          <h1>No receipts Found.. Please Upload a Receipt</h1>

          <!-- if there are receipts fetch them all-->
        {:else}
          <!-- {#key} block to force DOM re-creation when your data changes warning: could degrade performance -->
          {#key receipts.length}
            <!-- Loop over receipts -->
            {#each receipts as receipt}
              <div class="flex justify-center">
                <!-- TODO: Animation doesnt work after uploading.. only on mount-->
                <Card
                  class="receipt-card my-3 flex w-full flex-col duration-500 animate-in fade-in "
                >
                  <CardHeader class="flex flex-row justify-between gap-5">
                    <div class="flex flex-col gap-2">
                      <CardTitle
                        >{receipt.merchantName ? receipt?.merchantName : 'Merchant'}</CardTitle
                      >
                      <CardDescription>{receipt?.category || 'Other'}</CardDescription>
                    </div>
                    <div class="flex">
                      <ReceiptEdit {receipt} />
                    </div>
                  </CardHeader>

                  <!-- the Card Content -->
                  <ReceiptCardContent {receipt} />
                  <!-- todo i need the footer to be at very bottom of card  -->
                  <CardFooter class="">
                    <!-- TODO: Onclick Expand or popup Detailed view -->
                    <ReceiptDetails {receipt} />
                  </CardFooter>
                </Card>
              </div>
            {/each}
          {/key}
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
</style>
