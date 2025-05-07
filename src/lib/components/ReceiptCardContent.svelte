<script lang="ts">
  // Import shadcn components
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
  import { Separator } from './ui/separator';
  import { convertArabicToEnglishNumbers } from '../utils';

  // Import ReceiptData type
  import type { ReceiptData } from '../../types';
  import type { HTMLAttributes } from 'svelte/elements';
  import { cn } from '../utils';

  // Define props
  type $$Props = HTMLAttributes<HTMLDivElement> & {
    receipt: ReceiptData;
  };

  // Add receipt prop
  export let receipt: ReceiptData;
  let className: $$Props['class'] = undefined;
  export { className as class };

  // Format date to MM/DD/YYYY
  function formatDate(dateStr: string | undefined): string | null {
    if (!dateStr) return null;

    // First convert any Arabic/Persian numerals to English
    dateStr = convertArabicToEnglishNumbers(dateStr);

    try {
      // Handle different date formats (yyyy-mm-dd, dd.mm.yyyy, dd-mm-yyyy)
      let date: Date;

      // Check if date has dots (dd.mm.yyyy)
      if (dateStr.includes('.')) {
        const parts = dateStr.split('.');
        if (parts.length === 3) {
          // Assume dd.mm.yyyy format
          date = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
        } else {
          date = new Date(dateStr);
        }
      }
      // Check if date has dashes but in dd-mm-yyyy format
      else if (dateStr.includes('-') && dateStr.length <= 10 && !dateStr.match(/^\d{4}-/)) {
        const parts = dateStr.split('-');
        if (parts.length === 3) {
          // Assume dd-mm-yyyy format
          date = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
        } else {
          date = new Date(dateStr);
        }
      }
      // Standard format or other formats
      else {
        date = new Date(dateStr);
      }

      if (isNaN(date.getTime())) return null;

      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();

      return `${month}/${day}/${year}`;
    } catch (error) {
      return null;
    }
  }

  // Helper function to check if field has value
  function hasValue(field: any): boolean {
    return (
      field !== undefined &&
      field !== null &&
      field !== '' &&
      field !== 'unknown' &&
      field !== 'Unknown'
    );
  }

  //todo(show if jpy yen / euro /$ dollar/ riyal. only) Helper function to remove dollar sign if present and handle any input type
  function removeSign(value: any): string {
    if (value === undefined || value === null) return '';
    // Convert to string
    const strValue = String(value);
    // Convert any Arabic/Persian numerals to English before processing
    const englishValue = convertArabicToEnglishNumbers(strValue);
    // Remove $ and any non-numeric characters except decimal point
    return String(englishValue).replace(/[^\d.]/g, '');
  }
  // todo format numbers to be 100,000,000.00 in this format
  function formatNumber(value: any): string {}

  // Convert any value to string safely
  function safeString(value: any): string {
    if (value === undefined || value === null) return '';
    return String(value);
  }
</script>

<main class={className}>
  <div class="grid h-full gap-6">
    <!-- (auto-fit) stacks receipt in the row infinitly if there is space (350px each receipt) -->
    <div class="grid h-full grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-10">
      <div class="flex h-full justify-center">
        <CardContent class="flex h-full max-h-[800px] w-full max-w-md flex-col">
          <!-- Top section: Image and details -->
          <div class="flex-grow">
            <div
              class="mb-4 flex aspect-square w-full items-center justify-center overflow-hidden rounded-md bg-muted"
            >
              <!-- TODO: onclick img expand (done) & show retake option (still) -->
              <img
                class="h-full w-full object-cover"
                src={receipt.imageUrl || '/src/assets/contoso-receipt.png'}
                alt=""
              />
            </div>
            <div class="space-y-2">
              {#if hasValue(receipt?.category)}
                <div class="flex justify-between gap-2">
                  <span class="text-muted-foreground">Category</span>
                  <span>{receipt.category}</span>
                </div>
              {/if}
              <!-- Format date and only show if available -->
              {#if receipt?.date}
                {@const formattedDate = formatDate(receipt.date)}
                {#if formattedDate}
                  <div class="flex justify-between gap-2">
                    <span class="text-muted-foreground">Purchase Date</span>
                    <span class="font-size-sm">{formattedDate}</span>
                  </div>
                {/if}
              {/if}
              {#if hasValue(receipt?.vendor?.phone || receipt?.phone)}
                <div class="flex justify-between gap-2">
                  <span class="text-muted-foreground">Contact</span>
                  <span>
                    <a href="tel:{String(receipt.vendor?.phone || receipt.phone || '')}">
                      {String(receipt.vendor?.phone || receipt.phone || '')}
                    </a>
                  </span>
                </div>
              {/if}
              <!-- tax  -->
              <!-- {#if hasValue(receipt?.tax || receipt?.totalTax)}
                <div class="flex justify-between gap-2">
                  <span class="text-muted-foreground">Tax</span>
                  <div class="flex items-center justify-center gap-1">
                    <span class="flex gap-1">
                      {removeSign(safeString(receipt.tax || receipt.totalTax))}
                    </span>
                    <span>
                      {#if String(receipt?.total || '').includes('$') || (receipt?.line_items?.[0] && 'currency' in receipt.line_items[0] && receipt.line_items[0].currency === 'USD') || (receipt?.items?.[0] && 'currency' in receipt.items[0] && receipt.items[0].currency === 'USD')}
                        $
                      {:else}
                        <svg
                          class=" w-[15px] fill-white"
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
                      {/if}
                    </span>
                  </div>
                </div>
              {/if} -->

              <!-- Payment Method -->
              <div class="flex justify-between gap-2">
                <span class="text-muted-foreground">Payment Method</span>
                <span
                  >{receipt.payment?.display_name ||
                    (receipt.payment && 'method' in receipt.payment
                      ? receipt.payment.method
                      : 'Card')}</span
                >
              </div>

              {#if hasValue(receipt?.subtotal) && receipt.subtotal != 0}
                <div class="flex justify-between gap-2">
                  <span class="text-muted-foreground">Subtotal</span>
                  <!-- make riyal curr conditional: if currency is SA || empty , otherwise give dollar sign -->
                  <div class="flex items-center justify-center gap-1">
                    <span class="flex gap-1"
                      >{removeSign(receipt.subtotal)}
                      <!-- change color based on theme white/black | also confitional if saudi receipt, or includes"$" then remove -->
                    </span>
                    <span>
                      {#if String(receipt?.total).includes('$') || receipt?.items?.[0]?.currency === 'USD'}
                        $
                      {:else}
                        <svg
                          class=" w-[15px] fill-white"
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
                      {/if}
                    </span>
                  </div>
                </div>
              {/if}
              <!-- todo? -->
              <div class="flex justify-center">
                <span class="flex items-center justify-center text-muted-foreground">
                  <!-- <svg xmlns="http://www.w3.org/2000/svg" height="14" width="12.25" viewBox="0 0 448 512"><path d="M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l306.7 0L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z"/></svg>   -->
                </span>
              </div>
            </div>
          </div>

          <!-- Bottom section: Separator and total -->
          <div class="mt-8">
            <Separator />

            {#if hasValue(receipt?.total)}
              <div class="mt-2 flex justify-between font-medium">
                <span class="text-xl font-semibold">Total:</span>
                <div class="flex items-center justify-center gap-1">
                  <span class="text-xl font-medium"
                    >{receipt?.total != 0
                      ? removeSign(safeString(receipt.total))
                      : removeSign(safeString(receipt.subtotal))}
                  </span>

                  <span>
                    {#if String(receipt?.total).includes('$') || receipt?.items?.[0]?.currency === 'USD'}
                      $
                    {:else}
                      <svg
                        class="w-[18px] fill-white"
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
                    {/if}
                  </span>
                </div>
              </div>
            {/if}
          </div>
        </CardContent>
      </div>
    </div>
  </div>
</main>

<style>
</style>
