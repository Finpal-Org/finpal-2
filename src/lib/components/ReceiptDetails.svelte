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
  function removeSign(value: string | undefined): string {
    if (!value) return '';
    // Convert any Arabic/Persian numerals to English before processing
    const englishValue = convertArabicToEnglishNumbers(value);
    // Remove $ and any non-numeric characters except decimal point
    return String(englishValue).replace(/[^\d.]/g, '');
  }

  // Function to handle warranty settings for an item
  function setItemWarranty(
    index: number,
    hasWarranty: boolean,
    periodValue: number | 'other',
    isPeriodInDays = false
  ) {
    if (!receipt.items || !receipt.items[index]) return;

    // Create warranty object if it doesn't exist
    if (!receipt.items[index].warranty) {
      receipt.items[index].warranty = {
        hasWarranty: false,
        periodMonths: 12,
        expiryDate: '',
        isCustomPeriodInDays: false
      };
    }

    receipt.items[index].warranty.hasWarranty = hasWarranty;
    receipt.items[index].warranty.isCustomPeriodInDays = isPeriodInDays;

    if (periodValue === 'other') {
      receipt.items[index].warranty.periodMonths = 'other';
      receipt.items[index].warranty.expiryDate = undefined;
    } else {
      // If the period is in months, convert to days for calculation
      const periodDays = isPeriodInDays ? periodValue : monthsToDays(periodValue);

      // Store the original period value (could be months or days)
      receipt.items[index].warranty.periodMonths = periodValue;

      // Calculate expiry date if warranty is enabled
      if (hasWarranty) {
        receipt.items[index].warranty.expiryDate = calculateWarrantyExpiry(
          receipt.date,
          receipt.createdTime,
          periodDays
        );
      } else {
        receipt.items[index].warranty.expiryDate = undefined;
      }
    }

    // TODO: Save changes to Firestore (future implementation)
  }

  // Get warranty status display class (for color indicators)
  function getWarrantyStatusClass(item: any): string {
    if (!item.warranty || !item.warranty.hasWarranty) {
      return 'text-muted-foreground';
    }

    if (!item.warranty.expiryDate) {
      return 'text-yellow-500';
    }

    const daysRemaining = getWarrantyDaysRemaining(item.warranty.expiryDate);

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
    if (!item.warranty || !item.warranty.hasWarranty) {
      return 'No Warranty';
    }

    if (!item.warranty.expiryDate) {
      return 'Warranty Active';
    }

    const daysRemaining = getWarrantyDaysRemaining(item.warranty.expiryDate);

    if (daysRemaining < 0) {
      return `Expired (${item.warranty.expiryDate})`;
    } else if (daysRemaining === 0) {
      return 'Expires today';
    } else if (daysRemaining === 10) {
      return '10 day remaining (' + item.warranty.expiryDate + ')';
    } else {
      return `${daysRemaining} days remaining (${item.warranty.expiryDate})`;
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
                <img
                  class="h-auto max-h-[40vh] w-auto rounded-md object-contain"
                  src="/src/assets/contoso-receipt.png"
                  alt="Receipt image"
                />
              </div>

              <div class="space-y-4">
                <h3 class="text-lg font-semibold">Basic Details</h3>
                <!-- todo add following:
 1-created date
 2-adress
 3-time
  -->
                <Table.Root>
                  <Table.Header>
                    <Table.Row>
                      <Table.Head>Property</Table.Head>
                      <Table.Head>Value</Table.Head>
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
                        <Table.Cell>{new Date(receipt.createdTime).toLocaleDateString()}</Table.Cell
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

                    {#if hasValue(receipt?.totalTax)}
                      <Table.Row>
                        <Table.Cell class="font-medium">VAT Total</Table.Cell>
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

                    <Table.Row>
                      <Table.Cell class="font-medium">Payment Method</Table.Cell>
                      <Table.Cell>Card</Table.Cell>
                    </Table.Row>

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

                <Separator />

                <!--todo error unknown Items table -->
                <h3 class="text-lg font-semibold">Item Details</h3>

                <Table.Root>
                  <Table.Header>
                    <Table.Row>
                      <Table.Head>Item</Table.Head>
                      <Table.Head>Quantity</Table.Head>
                      <Table.Head>Currency</Table.Head>
                      <Table.Head>Amount</Table.Head>
                      <Table.Head>Warranty</Table.Head>
                      <Table.Head>Period</Table.Head>
                      <Table.Head>Status</Table.Head>
                      <Table.Head>Image</Table.Head>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                    <!--todo remove Debug line -->
                    <!-- {#if receipt.items && receipt.items.length > 0}
                      <Table.Row>
                        <Table.Cell class="text-xs text-muted-foreground">
                          Debug: {JSON.stringify(receipt.items[0])}
                        </Table.Cell>
                      </Table.Row>
                    {/if} -->
                    {#if receipt.items && receipt.items.length > 0}
                      {#each receipt.items as item, index}
                        <Table.Row>
                          <Table.Cell>{item?.description || 'unknown'}</Table.Cell>
                          <Table.Cell>{item?.quantity || 'unknown'}</Table.Cell>
                          <!-- todo receipt currency != item currency -->
                          <Table.Cell class="text-center">
                            {#if item?.currency === 'USD'}
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
                          <Table.Cell>{item?.amount || 'unknown'}</Table.Cell>
                          <Table.Cell>
                            <Select.Root
                              selected={item?.warranty?.hasWarranty
                                ? { value: 'yes', label: 'Yes' }
                                : { value: 'no', label: 'No' }}
                              onSelectedChange={(selected) => {
                                if (selected) {
                                  const hasWarranty = selected.value === 'yes';
                                  const period = item?.warranty?.periodMonths || 12;
                                  setItemWarranty(index, hasWarranty, period);
                                }
                              }}
                            >
                              <Select.Trigger>
                                <Select.Value placeholder="Has Warranty" />
                              </Select.Trigger>
                              <Select.Content>
                                <Select.Item value="yes">Yes</Select.Item>
                                <Select.Item value="no">No</Select.Item>
                              </Select.Content>
                            </Select.Root>
                          </Table.Cell>
                          <Table.Cell>
                            <Select.Root
                              selected={item?.warranty?.periodMonths
                                ? {
                                    value:
                                      typeof item.warranty.periodMonths === 'string'
                                        ? item.warranty.periodMonths
                                        : item.warranty.periodMonths.toString(),
                                    label:
                                      typeof item.warranty.periodMonths === 'string' &&
                                      item.warranty.periodMonths === 'other'
                                        ? 'Custom'
                                        : item.warranty?.isCustomPeriodInDays
                                          ? `${item.warranty.periodMonths} days`
                                          : `${item.warranty.periodMonths} months`
                                  }
                                : { value: '12', label: '12 M' }}
                              onSelectedChange={(selected) => {
                                if (selected) {
                                  const hasWarranty = item?.warranty?.hasWarranty || false;

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
                              <Select.Content>
                                <Select.Item value="12">12 M</Select.Item>
                                <Select.Item value="24">24 M</Select.Item>
                                <Select.Item value="36">36 M</Select.Item>
                                <Select.Item value="other">Custom (Days)</Select.Item>
                              </Select.Content>
                            </Select.Root>

                            {#if item?.warranty?.hasWarranty && item?.warranty?.periodMonths === 'other'}
                              <!-- The inline input is removed, now using dialog instead -->
                            {/if}
                          </Table.Cell>
                          <Table.Cell class={getWarrantyStatusClass(item)}>
                            {getWarrantyStatus(item)}
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
