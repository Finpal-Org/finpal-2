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
  import { Input } from './components/ui/input';
  import { Label } from './components/ui/label';
  import { Separator } from './components/ui/separator';
  import { getReceipts, receipts } from '../../firebase/fireStore.svelte';
  import { onMount } from 'svelte';
  import ReceiptUpload from './ReceiptUpload.svelte';
  import { fade, fly } from 'svelte/transition';
  import { backIn, backInOut } from 'svelte/easing';

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
      <div class="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-10">
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
              <div class=" flex justify-center">
                <!-- TODO: Animation doesnt work after uploading.. only on mount-->
                <Card
                  class="receipt-card my-3 flex w-full flex-col duration-500  animate-in  fade-in "
                >
                  <CardHeader>
                    <CardTitle>{receipt.merchantName ? receipt.merchantName : 'Merchant'}</CardTitle
                    >
                    <CardDescription>{receipt?.category || 'Other'}</CardDescription>
                  </CardHeader>
                  <CardContent class="flex-1">
                    <div
                      class="mb-4 flex aspect-square w-full items-center justify-center overflow-hidden rounded-md bg-muted"
                    >
                      <!-- TODO: onclick img expand & show retake option -->
                      <img
                        class="h-full w-full object-cover"
                        src="/src/assets/contoso-receipt.png"
                        alt=""
                      />
                    </div>

                    <div class="space-y-2">
                      <div class="flex justify-between gap-2">
                        <span class="text-muted-foreground">Category</span>
                        <span>{receipt?.category || 'N/A'}</span>
                      </div>

                      <!-- todo move address inside details  -->
                      <div class="flex justify-between gap-2">
                        <span class="text-muted-foreground">Date</span>
                        <span class="font-size-sm">{receipt?.date || 'N/A'}</span>
                      </div>

                      <div class="flex justify-between gap-2">
                        <span class="text-muted-foreground">Contact</span>
                        <!-- TODO: needs proper phone formating for quick access (copy paste) -->
                        <span
                          ><a href="tel:{receipt?.phone || 'N/A'}">
                            {receipt?.phone || 'N/A'}</a
                          ></span
                        >
                      </div>

                      <div class="flex justify-between gap-2">
                        <!-- PAYMENT METHOD TODO: -->
                        <span class="text-muted-foreground">Vat Total</span>
                        <!-- make riyal curr conditional: if currency is SA || empty , otherwise give dollar sign -->
                        <span class="flex gap-1"
                          >{receipt?.totalTax || 'N/A'}
                          <!-- change color based on theme white/black | also confitional if saudi receipt, or includes"$" then remove -->
                          <svg
                            class="w-[15px] fill-white"
                            xmlns="http://www.w3.org/2000/svg"
                            id="Layer_1"
                            data-name="Layer 1"
                            viewBox="0 0 1124.14 1256.39"
                          >
                            <path
                              class=""
                              d="M699.62,1113.02h0c-20.06,44.48-33.32,92.75-38.4,143.37l424.51-90.24c20.06-44.47,33.31-92.75,38.4-143.37l-424.51,90.24Z"
                            />
                            <path
                              class=""
                              d="M1085.73,895.8c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.33v-135.2l292.27-62.11c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.27V66.13c-50.67,28.45-95.67,66.32-132.25,110.99v403.35l-132.25,28.11V0c-50.67,28.44-95.67,66.32-132.25,110.99v525.69l-295.91,62.88c-20.06,44.47-33.33,92.75-38.42,143.37l334.33-71.05v170.26l-358.3,76.14c-20.06,44.47-33.32,92.75-38.4,143.37l375.04-79.7c30.53-6.35,56.77-24.4,73.83-49.24l68.78-101.97v-.02c7.14-10.55,11.3-23.27,11.3-36.97v-149.98l132.25-28.11v270.4l424.53-90.28Z"
                            />
                          </svg>
                        </span>
                      </div>

                      <!-- PAYMENT METHOD TODO: -->
                      <div class="flex justify-between gap-2">
                        <span class="text-muted-foreground">Payment Method</span>
                        <span>{'Card'}</span>
                      </div>

                      <!-- Items : Loop if there is more than 1 item-->
                      {#if receipt.items}
                        {#each receipt.items as item}
                          <div class="flex justify-between gap-2">
                            <span class="text-muted-foreground">Item</span>
                            <div class="flex flex-col gap-1">
                              <span>{item?.description || 'unknown'}</span>
                              <span>{item?.quantity || 'unknown'}</span>
                              <span>{item?.currency || 'unknown'}</span>
                              <span>{item?.amount || 'unknown'}</span>
                            </div>
                          </div>
                        {/each}
                      {/if}
                      <!-- todo? -->
                      <div class="flex justify-center">
                        <span class="flex items-center justify-center text-muted-foreground">
                          <!-- <svg xmlns="http://www.w3.org/2000/svg" height="14" width="12.25" viewBox="0 0 448 512"><path d="M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l306.7 0L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z"/></svg>   -->
                        </span>
                      </div>

                      <Separator />

                      <div class="flex justify-between font-medium">
                        <span>Total:</span>
                        <span>{receipt?.total || 'N/A'}</span>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter class="">
                    <!-- TODO: Onclick Expand or popup Detailed view -->
                    <Button size="sm" class="w-full">View Details</Button>
                  </CardFooter>
                </Card>
              </div>
            {/each}
          {/key}
        {/if}

        <!-- Receipt 2 - using hardcoded sample data -->
        <!-- <Card>
        <CardHeader>
          <CardTitle>{sampleReceipt.merchantName.value}</CardTitle>
          <CardDescription>{sampleReceipt.date.value}</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
            <span class="text-muted-foreground">Receipt Image</span>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Category:</span>
              <span>{sampleReceipt.category.value}</span>
            </div>
            <Separator />
            <div class="flex justify-between font-medium">
              <span>Total:</span>
              <span>{sampleReceipt.total.value}</span>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button  size="lg" class="w-full">View Details</Button>
        </CardFooter>
      </Card> -->
      </div>
    </div>
  </div>
</main>

<style>
</style>
