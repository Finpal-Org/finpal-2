<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Button } from './ui/button';
  import { Input } from './ui/input';
  import { Label } from './ui/label';
  import * as Select from './ui/select/index';
  import type { ReceiptData } from '../../types';
  import ReceiptCardContent from './ReceiptCardContent.svelte';
  import CardContent from './ui/card/card-content.svelte';
  import Separator from './ui/separator/separator.svelte';
  import * as Table from './ui/table/index';
  import {
    calculateWarrantyExpiry,
    isWarrantyExpired,
    getWarrantyDaysRemaining,
    formatDate as formatDateUtil,
    monthsToDays
  } from '../utils/warrantyUtils';
  import { convertArabicToEnglishNumbers } from '../utils';

  // Add receipt prop
  export let receipt: ReceiptData;

  // State to manage custom days dialog
  let showCustomDaysDialog = false;
  let currentItemIndex = -1;
  let customDaysValue = '';

  // State for image dialog
  let showImageDialog = false;
  let currentImageUrl = '';

  // Format date to DD/MM/YYYY
  function formatDate(dateStr: string | undefined): string | null {
    return formatDateUtil(dateStr);
  }

  // Open custom days dialog for a specific item
  function openCustomDaysDialog(index: number) {
    currentItemIndex = index;
    customDaysValue = '';
    showCustomDaysDialog = true;
  }

  // Save custom days value and close dialog
  function saveCustomDays() {
    const days = parseInt(customDaysValue);
    if (!isNaN(days) && days > 0 && currentItemIndex >= 0) {
      handleCustomWarrantyDays(currentItemIndex, days);
    }
    showCustomDaysDialog = false;
  }

  // Cancel custom days dialog
  function cancelCustomDays() {
    showCustomDaysDialog = false;
  }

  // Open image in dialog
  function openImageDialog(imageUrl: string) {
    currentImageUrl = imageUrl;
    showImageDialog = true;
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

  // Helper function to remove dollar sign if present
  function removeSign(value: string | number | undefined): string {
    if (!value) return '';
    // Convert any Arabic/Persian numerals to English before processing
    const englishValue = convertArabicToEnglishNumbers(String(value));
    // Remove $ and any non-numeric characters except decimal point
    return String(englishValue).replace(/[^\d.]/g, '');
  }

  // Get items array from either structure for displaying
  function getDisplayItems() {
    if (receipt.line_items && receipt.line_items.length > 0) {
      return receipt.line_items;
    }
    return receipt.items || [];
  }

  // Function to get warranty status for an item
  function getItemWarranty(item: any) {
    return item.warranty || { hasWarranty: false, periodMonths: 12 };
  }

  // Function to handle warranty settings for an item
  function setItemWarranty(
    index: number,
    hasWarranty: boolean,
    periodValue: number | 'other',

    isPeriodInDays = false
  ) {
    const items = getDisplayItems();
    if (!items || !items[index]) return;

    // Initialize warranty if it doesn't exist
    if (!items[index].warranty) {
      items[index].warranty = {
        hasWarranty: false,
        periodMonths: 12,
        expiryDate: '',
        isCustomPeriodInDays: false
      };
    }

    const warranty = items[index].warranty;
    warranty.hasWarranty = hasWarranty;
    warranty.isCustomPeriodInDays = isPeriodInDays;

    if (periodValue === 'other') {
      warranty.periodMonths = 'other';
      warranty.expiryDate = undefined;
    } else {
      // If the period is in months, convert to days for calculation
      const periodDays = isPeriodInDays ? periodValue : monthsToDays(periodValue);

      // Store the original period value (could be months or days)
      warranty.periodMonths = periodValue;

      // Calculate expiry date if warranty is enabled
      if (hasWarranty) {
        warranty.expiryDate = calculateWarrantyExpiry(
          receipt.date,
          receipt.createdTime,
          periodDays
        );
      } else {
        warranty.expiryDate = undefined;
      }
    }

    // TODO: Save changes to Firestore (future implementation)
  }

  // Get warranty status display class (for color indicators)
  function getWarrantyStatusClass(item: any): string {
    const warranty = getItemWarranty(item);

    if (!warranty.hasWarranty) {
      return 'text-muted-foreground';
    }

    if (!warranty.expiryDate) {
      return 'text-yellow-500';
    }

    const daysRemaining = getWarrantyDaysRemaining(warranty.expiryDate);

    if (daysRemaining < 0) {
      return 'text-red-500'; // Expired
    } else if (daysRemaining <= 10) {
      return 'text-yellow-500'; // Less than 10 days remaining
    } else {
      return 'text-green-500'; // More than 10 days remaining
    }
  }

  // Get human-readable warranty status
  function getWarrantyStatus(item: any): string {
    const warranty = getItemWarranty(item);

    if (!warranty.hasWarranty) {
      return 'No Warranty';
    }

    if (!warranty.expiryDate) {
      return 'Warranty Active';
    }

    const daysRemaining = getWarrantyDaysRemaining(warranty.expiryDate);

    if (daysRemaining < 0) {
      return `Expired (${warranty.expiryDate})`;
    } else if (daysRemaining === 0) {
      return 'Expires today';
    } else if (daysRemaining === 10) {
      return '10 day remaining (' + warranty.expiryDate + ')';
    } else {
      return `${daysRemaining} days remaining (${warranty.expiryDate})`;
    }
  }

  // Handle custom warranty period in days
  function handleCustomWarrantyDays(index: number, days: number) {
    if (days > 0) {
      setItemWarranty(index, true, days, true);
    }
  }
</script>

<!-- Custom Days Dialog -->
{#if showCustomDaysDialog}
  <Dialog.Root open={showCustomDaysDialog}>
    <Dialog.Content class="sm:max-w-[425px]">
      <Dialog.Header>
        <Dialog.Title>Custom Warranty Period</Dialog.Title>
        <Dialog.Description>Enter warranty period in days.</Dialog.Description>
      </Dialog.Header>
      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-4 items-center gap-4">
          <Label class="text-right">Days</Label>
          <Input
            type="number"
            min="1"
            class="col-span-3"
            placeholder="Enter days"
            bind:value={customDaysValue}
          />
        </div>
      </div>
      <Dialog.Footer>
        <Button variant="outline" on:click={cancelCustomDays}>Cancel</Button>
        <Button on:click={saveCustomDays}>Save</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Root>
{/if}

<!-- Image Dialog -->
{#if showImageDialog}
  <Dialog.Root open={showImageDialog} onOpenChange={(open) => (showImageDialog = open)}>
    <Dialog.Content class="max-w-4xl">
      <Dialog.Header>
        <Dialog.Title>Receipt Image</Dialog.Title>
      </Dialog.Header>
      <div class="flex justify-center p-4">
        <img
          src={currentImageUrl}
          alt="Receipt image full view"
          class="max-h-[80vh] w-auto rounded-md object-contain"
        />
      </div>
      <Dialog.Footer>
        <Button on:click={() => (showImageDialog = false)}>Close</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Root>
{/if}

<main class="w-full">
  <Dialog.Root>
    <Dialog.Trigger class=" w-full ">
      <Button size="lg" class=" w-full">View Details</Button>
    </Dialog.Trigger>
    <Dialog.Content class="max-h-[90vh] max-w-[90vw] overflow-y-auto">
      <Dialog.Header>
        <Dialog.Title>Receipt Details</Dialog.Title>
      </Dialog.Header>
      <Dialog.Description>
        <div class="grid gap-6">
          <!-- <Separator /> -->
          <!-- (auto-fit) stacks receipt in the row infinitly if there is space (350px each receipt) -->
          <!-- <div class="grid grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-10"> -->
          <div class=" flex justify-center">
            <CardContent class="flex-1">
              <div class="mx-auto my-4 flex w-full max-w-md justify-center">
                <div
                  class="cursor-pointer"
                  on:click={() =>
                    openImageDialog(receipt.imageUrl || '/src/assets/contoso-receipt.png')}
                  on:keydown={(e) =>
                    e.key === 'Enter' &&
                    openImageDialog(receipt.imageUrl || '/src/assets/contoso-receipt.png')}
                  tabindex="0"
                >
                  <img
                    class="h-auto max-h-[40vh] w-auto rounded-md object-contain transition-opacity hover:opacity-80"
                    src={receipt.imageUrl || '/src/assets/contoso-receipt.png'}
                    alt="Receipt image"
                  />
                </div>
              </div>

              <div class="space-y-4">
                <h3 class="text-2xl font-semibold text-green-500">Basic Details</h3>
                <!-- todo add following:
 1-created date
 2-adress
 3-time
  -->
                <!-- todo lets try to put 2 table.roots side by side flex-row  -->
                <div class="flex flex-row">
                  <Table.Root>
                    <Table.Header>
                      <Table.Row>
                        <Table.Head class="text-lg">Field</Table.Head>
                        <!-- <Table.Head>Value</Table.Head> -->
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {#if hasValue(receipt?.category)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Category</Table.Cell>
                          <Table.Cell>{receipt.category}</Table.Cell>
                        </Table.Row>
                      {/if}

                      {#if receipt?.date}
                        {@const formattedDate = formatDate(receipt.date)}
                        {#if formattedDate}
                          <Table.Row>
                            <Table.Cell class="font-medium">Date</Table.Cell>
                            <Table.Cell>{formattedDate}</Table.Cell>
                          </Table.Row>
                        {/if}
                      {/if}

                      {#if receipt?.createdTime}
                        <Table.Row>
                          <Table.Cell class="font-medium">Added On</Table.Cell>
                          <Table.Cell
                            >{new Date(receipt.createdTime).toLocaleDateString()}</Table.Cell
                          >
                        </Table.Row>
                      {/if}

                      {#if hasValue(receipt?.address)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Address</Table.Cell>
                          <!-- address might not need arabic -> english numbers -->
                          <Table.Cell
                            >{receipt.address
                              ? convertArabicToEnglishNumbers(receipt.address)
                              : ''}</Table.Cell
                          >
                        </Table.Row>
                      {/if}

                      {#if hasValue(receipt?.phone)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Contact</Table.Cell>
                          <Table.Cell>
                            <a
                              href="tel:{receipt.phone
                                ? convertArabicToEnglishNumbers(receipt.phone)
                                : ''}"
                            >
                              {receipt.phone ? convertArabicToEnglishNumbers(receipt.phone) : ''}
                            </a>
                          </Table.Cell>
                        </Table.Row>
                      {/if}

                      <Table.Row>
                        <Table.Cell class="font-medium">Payment Method</Table.Cell>
                        <Table.Cell>Card</Table.Cell>
                      </Table.Row>

                      {#if hasValue(receipt?.totalTax)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Tax</Table.Cell>
                          <Table.Cell class="flex items-center gap-2">
                            {removeSign(receipt.totalTax)}
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
                          </Table.Cell>
                        </Table.Row>
                      {/if}

                      {#if hasValue(receipt?.subtotal)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Subtotal</Table.Cell>
                          <Table.Cell class="flex items-center gap-2">
                            {removeSign(receipt.subtotal)}
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
                          </Table.Cell>
                        </Table.Row>
                      {/if}

                      {#if hasValue(receipt?.total)}
                        <Table.Row>
                          <Table.Cell class="text-xl font-medium">Total</Table.Cell>
                          <Table.Cell class="flex items-center gap-2 text-xl">
                            {removeSign(receipt.total)}
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
                          </Table.Cell>
                        </Table.Row>
                      {/if}
                    </Table.Body>
                  </Table.Root>
                  <!-- todo 2nd table: add rest of fields from azure 4.0 .. overwhelm fields here -->
                  <Table.Root>
                    <Table.Header>
                      <Table.Row>
                        <Table.Head class="text-lg">Field</Table.Head>
                        <!-- <Table.Head>Value</Table.Head> -->
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {#if hasValue(receipt?.tip)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Tip</Table.Cell>
                          <Table.Cell>{receipt.tip}</Table.Cell>
                        </Table.Row>
                      {/if}

                      {#if hasValue((receipt as any)?.countryRegion)}
                        <Table.Row>
                          <Table.Cell class="font-medium">Country</Table.Cell>
                          <Table.Cell>{(receipt as any).countryRegion}</Table.Cell>
                        </Table.Row>
                      {/if}

                      {#if (receipt as any)?.taxDetailsArray && (receipt as any).taxDetailsArray.length > 0}
                        <Table.Row>
                          <Table.Cell class="font-medium">Tax Details</Table.Cell>
                          <Table.Cell>
                            <div class="space-y-2">
                              {#each (receipt as any).taxDetailsArray as taxDetail, index}
                                <div class="rounded bg-secondary/30 p-1 text-sm">
                                  {#if taxDetail.description}
                                    <div>
                                      <span class="font-semibold">Description:</span>
                                      {taxDetail.description}
                                    </div>
                                  {/if}
                                  {#if taxDetail.rate}
                                    <div>
                                      <span class="font-semibold">Rate:</span>
                                      {taxDetail.rate}
                                    </div>
                                  {/if}
                                  {#if taxDetail.netAmount}
                                    <div>
                                      <span class="font-semibold">Net Amount:</span>
                                      {taxDetail.netAmount}
                                    </div>
                                  {/if}
                                </div>
                              {/each}
                            </div>
                          </Table.Cell>
                        </Table.Row>
                      {/if}
                    </Table.Body>
                  </Table.Root>
                </div>

                <Separator />

                <!--todo error unknown Items table -->
                <h3 class="text-2xl font-semibold text-green-500">Item Details</h3>

                <Table.Root>
                  <Table.Header>
                    <Table.Row>
                      <Table.Head>Item</Table.Head>
                      <Table.Head>Quantity</Table.Head>
                      <Table.Head>Currency</Table.Head>
                      <Table.Head>Amount</Table.Head>
                      <Table.Head>Warranty</Table.Head>
                      {#if getDisplayItems().some((item) => getItemWarranty(item).hasWarranty)}
                        <Table.Head>Period</Table.Head>
                      {/if}
                      <Table.Head>Status</Table.Head>
                      <Table.Head>Image</Table.Head>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                    {#if getDisplayItems().length > 0}
                      {#each getDisplayItems() as item, index}
                        <Table.Row>
                          <Table.Cell>{item?.description || 'unknown'}</Table.Cell>
                          <Table.Cell>{item?.quantity || '-'}</Table.Cell>
                          <!-- Currency display -->
                          <Table.Cell class="text-center">
                            {#if item?.currency === 'USD' || receipt?.currency === 'USD'}
                              $
                            {:else}
                              <div class="h m-0 flex items-center justify-center">
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
                              </div>
                            {/if}
                          </Table.Cell>
                          <Table.Cell>{item?.amount || item?.total || 'unknown'}</Table.Cell>
                          <Table.Cell>
                            <Select.Root
                              selected={getItemWarranty(item).hasWarranty
                                ? { value: 'yes', label: 'Yes' }
                                : { value: 'no', label: 'No' }}
                              onSelectedChange={(selected) => {
                                if (selected) {
                                  const hasWarranty = selected.value === 'yes';
                                  const period = getItemWarranty(item).periodMonths || 12;
                                  setItemWarranty(index, hasWarranty, period);
                                }
                              }}
                            >
                              <!--todo make has warranty be saved with its expiry date, optionally add simple notifcation once in app locally  for user if <10 remaining. do it simply first maybe a i icon on corner of receipt or simple notifcation icon in @navbar  -->
                              <Select.Trigger>
                                <Select.Value placeholder="Has Warranty" />
                              </Select.Trigger>
                              <Select.Content style="--height: auto; --max-height: none;">
                                <Select.Item value="yes">Yes</Select.Item>
                                <Select.Item value="no">No</Select.Item>
                              </Select.Content>
                            </Select.Root>
                          </Table.Cell>
                          {#if getItemWarranty(item).hasWarranty}
                            <Table.Cell>
                              <Select.Root
                                selected={getItemWarranty(item).periodMonths
                                  ? {
                                      value:
                                        typeof getItemWarranty(item).periodMonths === 'string'
                                          ? getItemWarranty(item).periodMonths
                                          : getItemWarranty(item).periodMonths.toString(),
                                      label:
                                        typeof getItemWarranty(item).periodMonths === 'string' &&
                                        getItemWarranty(item).periodMonths === 'other'
                                          ? 'Custom'
                                          : getItemWarranty(item).isCustomPeriodInDays
                                            ? `${getItemWarranty(item).periodMonths} days`
                                            : `${getItemWarranty(item).periodMonths} months`
                                    }
                                  : { value: '12', label: '12 M' }}
                                onSelectedChange={(selected) => {
                                  if (selected) {
                                    const hasWarranty = getItemWarranty(item).hasWarranty || false;

                                    if (selected.value === 'other') {
                                      // Open custom days dialog instead of setting directly
                                      openCustomDaysDialog(index);
                                    } else {
                                      const period = parseInt(selected.value);
                                      setItemWarranty(index, hasWarranty, period);
                                    }
                                  }
                                }}
                              >
                                <Select.Trigger>
                                  <Select.Value placeholder="Select Period" />
                                </Select.Trigger>
                                <Select.Content style="--height: auto; --max-height: none;">
                                  <Select.Item value="12">12 M</Select.Item>
                                  <Select.Item value="24">24 M</Select.Item>
                                  <Select.Item value="36">36 M</Select.Item>
                                  <Select.Item value="other">Custom (Days)</Select.Item>
                                </Select.Content>
                              </Select.Root>
                            </Table.Cell>
                          {:else if getDisplayItems().some((i) => getItemWarranty(i).hasWarranty)}
                            <Table.Cell></Table.Cell>
                          {/if}
                          <Table.Cell class={getWarrantyStatusClass(item)}>
                            {getWarrantyStatus(item)}
                          </Table.Cell>
                          <!-- Image cell -->
                          <Table.Cell>
                            <div
                              class="cursor-pointer"
                              on:click={() =>
                                openImageDialog(
                                  receipt.imageUrl || '/src/assets/contoso-receipt.png'
                                )}
                              on:keydown={(e) =>
                                e.key === 'Enter' &&
                                openImageDialog(
                                  receipt.imageUrl || '/src/assets/contoso-receipt.png'
                                )}
                              tabindex="0"
                            >
                              <img
                                class="rouded-sm h-auto max-h-[100px] max-w-[100px] object-contain transition-opacity hover:opacity-80"
                                src={receipt.imageUrl || '/src/assets/contoso-receipt.png'}
                                alt="Receipt image"
                              />
                            </div>
                          </Table.Cell>
                        </Table.Row>
                      {/each}
                    {/if}
                  </Table.Body>
                </Table.Root>
              </div>
            </CardContent>
          </div>
        </div>
        <!-- </div> -->
      </Dialog.Description>
    </Dialog.Content>
  </Dialog.Root>
</main>
