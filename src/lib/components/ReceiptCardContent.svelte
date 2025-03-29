<script lang="ts">
  // Import shadcn components
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
  import { Separator } from './ui/separator';

  // Import ReceiptData type
  import type { ReceiptData } from '../../types';

  // Add receipt prop
  export let receipt: ReceiptData;
</script>

<main>
  <div class="grid gap-6">
    <!-- <Separator /> -->
    <!-- (auto-fit) stacks receipt in the row infinitly if there is space (350px each receipt) -->
    <div class="grid grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-10">
      <div class=" flex justify-center">
        <CardContent class="flex-1">
          <div
            class="mb-4 flex aspect-square w-full items-center justify-center overflow-hidden rounded-md bg-muted"
          >
            <!-- TODO: onclick img expand & show retake option -->
            <img class="h-full w-full object-cover" src="/src/assets/contoso-receipt.png" alt="" />
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
              <span><a href="tel:{receipt?.phone || 'N/A'}"> {receipt?.phone || 'N/A'}</a></span>
            </div>

            <div class="flex justify-between gap-2">
              <!-- PAYMENT METHOD TODO: -->
              <span class="text-muted-foreground">Vat Total</span>
              <!-- make riyal curr conditional: if currency is SA || empty , otherwise give dollar sign -->
              <span class="flex gap-1"
                >{receipt?.totalTax || 'N/A'}
                <!-- change color based on theme white/black | also confitional if saudi receipt, or includes"$" then remove -->
              </span>
            </div>

            <!-- PAYMENT METHOD TODO: -->
            <div class="flex justify-between gap-2">
              <span class="text-muted-foreground">Payment Method</span>
              <span>{'Card'}</span>
            </div>

            <!--TODO Items : Loop if there is more than 1 item-->
            <!-- {#if receipt.items}
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
            {/if} -->
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
      </div>
    </div>
  </div>
</main>

<style>
</style>
