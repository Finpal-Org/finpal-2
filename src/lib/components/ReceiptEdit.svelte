<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Label } from './ui/label';
  import { Input } from './ui/input';
  import { Button } from './ui/button';
  import type { ReceiptData } from '../../types';
  import { Separator } from './ui/separator';
  import * as Select from './ui/select/index';
  import * as Table from './ui/table/index';
  import { standardCategories } from '../utils/categoryMapping';
  import { calculateWarrantyExpiry, monthsToDays } from '../utils/warrantyUtils';
  import { createEventDispatcher } from 'svelte';
  import type { Selected } from 'bits-ui';
  import { convertArabicToEnglishNumbers } from '../utils';

  // Define props with proper typing
  interface $$Props {
    receipt: ReceiptData;
  }

  // Use $props() for Svelte 5 runes
  const receipt = $props();

  // Create dispatch for save event
  const dispatch = createEventDispatcher();

  // State for custom days dialog
  let showCustomDaysDialog = false;
  let currentItemIndex = -1;
  let customDaysValue = '';

  // Form state - only include fields from ReceiptData interface
  let formData = $state({
    merchantName: receipt?.merchantName || '',
    category: receipt?.category || '',
    phone: receipt?.phone || '',
    date: receipt?.date || '',
    time: receipt?.time || '',
    total: receipt?.total || '',
    totalTax: receipt?.totalTax || '',
    subtotal: receipt?.subtotal || '',
    address: receipt?.address || '',
    items: receipt?.items || []
  });

  // Track custom warranty period inputs
  let customWarrantyPeriods = $state(new Array(formData.items.length).fill(null));

  // Add state for custom days dialog
  let customDaysDialogOpen = false;
  let tempCustomDays = 0;

  // Add state for dialog visibility
  let dialogOpen = false;

  // Open custom days dialog
  function openCustomDaysDialog(index: number) {
    currentItemIndex = index;
    customDaysValue = '';
    showCustomDaysDialog = true;
  }

  // Save custom days value and close dialog
  function saveCustomDays() {
    const days = parseInt(customDaysValue);
    if (!isNaN(days) && days > 0 && currentItemIndex >= 0) {
      handleCustomWarrantyPeriod(currentItemIndex, days.toString());
    }
    showCustomDaysDialog = false;
  }

  // Cancel custom days dialog
  function cancelCustomDays() {
    showCustomDaysDialog = false;
    customDaysDialogOpen = false;
  }

  // Handle form submission
  async function handleSubmit(event: Event) {
    event.preventDefault();
    // TODO: Add form validation
    // TODO: Add API call to update receipt
    console.log('Form submitted:', formData);
    dispatch('save', formData);

    // Show success message (in a real app, this would come after API response)
    alert('Receipt updated successfully');

    // Close dialog by changing state
    dialogOpen = false;
  }

  // Handle item changes with proper typing
  function handleItemChange(index: number, field: keyof (typeof formData.items)[0], value: string) {
    if (!formData.items[index]) {
      formData.items[index] = {
        description: '',
        amount: '',
        currency: 'SAR',
        quantity: '',
        warranty: {
          hasWarranty: false,
          periodMonths: 12,
          expiryDate: undefined,
          isCustomPeriodInDays: false
        }
      };
    }
    formData.items[index][field] = value;
  }

  // Handle warranty settings for an item
  function handleWarrantyChange(
    index: number,
    hasWarranty: boolean,
    periodValue: number | 'other' = 12,
    isPeriodInDays = false
  ) {
    if (!formData.items[index]) return;

    // Create warranty object if it doesn't exist
    if (!formData.items[index].warranty) {
      formData.items[index].warranty = {
        hasWarranty: false,
        periodMonths: 12,
        expiryDate: undefined,
        isCustomPeriodInDays: false
      };
    }

    formData.items[index].warranty.hasWarranty = hasWarranty;
    formData.items[index].warranty.periodMonths = periodValue;
    formData.items[index].warranty.isCustomPeriodInDays = isPeriodInDays;

    // Calculate expiry date if warranty is enabled
    if (hasWarranty && receipt?.date && typeof periodValue === 'number') {
      // Convert period to days if it's in months
      const periodDays = isPeriodInDays ? periodValue : monthsToDays(periodValue);

      formData.items[index].warranty.expiryDate = calculateWarrantyExpiry(
        receipt.date,
        receipt.createdTime,
        periodDays
      );
    } else {
      formData.items[index].warranty.expiryDate = undefined;
    }
  }

  // Handle custom warranty period
  function handleCustomWarrantyPeriod(index: number, value: string) {
    const days = parseInt(value);
    if (!isNaN(days) && days > 0) {
      customWarrantyPeriods[index] = days;
      handleWarrantyChange(index, true, days, true);
    }
  }

  // Handle period selection
  function handlePeriodSelection(index: number, selected: Selected<string> | undefined) {
    if (selected) {
      if (selected.value === 'other') {
        openCustomDaysDialog(index);
      } else {
        const period = parseInt(selected.value);
        if (!isNaN(period)) {
          handleWarrantyChange(index, true, period);
        }
      }
    }
  }

  // Format date to DD/MM/YYYY
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

  // Helper function to remove dollar sign if present
  function removeSign(value: string | undefined): string {
    if (!value) return '';
    // Convert any Arabic/Persian numerals to English before processing
    const englishValue = convertArabicToEnglishNumbers(value);
    // Remove $ and any non-numeric characters except decimal point
    return String(englishValue).replace(/[^\d.]/g, '');
  }
</script>

<main>
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

  <Dialog.Root bind:open={dialogOpen}>
    <Dialog.Trigger on:click={() => (dialogOpen = true)}>
      <Button size="lg" variant="secondary" class="w-full text-green-500">Edit</Button>
    </Dialog.Trigger>
    <Dialog.Content class="max-h-[90vh] max-w-[90vw] overflow-y-auto">
      <Dialog.Header>
        <Dialog.Title>Edit Receipt</Dialog.Title>
      </Dialog.Header>
      <Dialog.Description>
        <form on:submit={handleSubmit} class="space-y-6">
          <div class="grid gap-6">
            <div class="flex justify-center">
              <div class="flex-1">
                <div class="mx-auto my-4 flex w-full max-w-md justify-center">
                  <img
                    class="h-auto max-h-[40vh] w-auto rounded-md object-contain"
                    src="/src/assets/contoso-receipt.png"
                    alt="Receipt image"
                  />
                </div>

                <!-- Basic Details Section -->
                <div class="space-y-4">
                  <h3 class="text-lg font-semibold">Basic Details</h3>
                  <Table.Root>
                    <Table.Header>
                      <Table.Row>
                        <Table.Head>Property</Table.Head>
                        <Table.Head>Value</Table.Head>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      <Table.Row>
                        <Table.Cell class="font-medium">Merchant Name</Table.Cell>
                        <Table.Cell>
                          <Input type="text" placeholder="N/A" bind:value={formData.merchantName} />
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Category</Table.Cell>
                        <Table.Cell>
                          <Select.Root
                            selected={formData.category
                              ? { value: formData.category, label: formData.category }
                              : undefined}
                            onSelectedChange={(selected) => {
                              if (selected) {
                                formData.category = selected.value;
                              }
                            }}
                          >
                            <Select.Trigger class="w-full">
                              <Select.Value placeholder="N/A" />
                            </Select.Trigger>
                            <Select.Content>
                              {#each standardCategories as category}
                                <Select.Item value={category} label={category}
                                  >{category}</Select.Item
                                >
                              {/each}
                            </Select.Content>
                          </Select.Root>
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Date</Table.Cell>
                        <Table.Cell>
                          <Input type="date" bind:value={formData.date} placeholder="N/A" />
                        </Table.Cell>
                      </Table.Row>

                      {#if receipt?.createdTime}
                        <Table.Row>
                          <Table.Cell class="font-medium">Added On</Table.Cell>
                          <Table.Cell
                            >{new Date(receipt.createdTime).toLocaleDateString()}</Table.Cell
                          >
                        </Table.Row>
                      {/if}

                      <Table.Row>
                        <Table.Cell class="font-medium">Address</Table.Cell>
                        <Table.Cell>
                          <Input type="text" bind:value={formData.address} placeholder="N/A" />
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Contact</Table.Cell>
                        <Table.Cell>
                          <Input type="tel" bind:value={formData.phone} placeholder="N/A" />
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Payment Method</Table.Cell>
                        <Table.Cell>
                          <Select.Root
                            selected={{ value: 'Card', label: 'Card' }}
                            onSelectedChange={(selected) => {
                              // Payment method handling
                            }}
                          >
                            <Select.Trigger class="w-full">
                              <Select.Value placeholder="N/A" />
                            </Select.Trigger>
                            <Select.Content>
                              <Select.Item value="Card">Card</Select.Item>
                              <Select.Item value="Cash">Cash</Select.Item>
                            </Select.Content>
                          </Select.Root>
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Tax</Table.Cell>
                        <Table.Cell class="flex items-center gap-2">
                          <Input
                            type="number"
                            bind:value={formData.totalTax}
                            placeholder="N/A"
                            class="w-full"
                          />
                          <span>
                            {#if String(formData?.total).includes('$') || formData?.items?.[0]?.currency === 'USD'}
                              $
                            {:else}
                              <svg
                                class="w-[15px] fill-white"
                                xmlns="http://www.w3.org/2000/svg"
                                id="Layer_1"
                                data-name="Layer 1"
                                viewBox="0 0 1124.14 1256.39"
                              >
                                <path
                                  d="M699.62,1113.02h0c-20.06,44.48-33.32,92.75-38.4,143.37l424.51-90.24c20.06-44.47,33.31-92.75,38.4-143.37l-424.51,90.24Z"
                                />
                                <path
                                  d="M1085.73,895.8c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.33v-135.2l292.27-62.11c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.27V66.13c-50.67,28.45-95.67,66.32-132.25,110.99v403.35l-132.25,28.11V0c-50.67,28.44-95.67,66.32-132.25,110.99v525.69l-295.91,62.88c-20.06,44.47-33.33,92.75-38.42,143.37l334.33-71.05v170.26l-358.3,76.14c-20.06,44.47-33.32,92.75-38.4,143.37l375.04-79.7c30.53-6.35,56.77-24.4,73.83-49.24l68.78-101.97v-.02c7.14-10.55,11.3-23.27,11.3-36.97v-149.98l132.25-28.11v270.4l424.53-90.28Z"
                                />
                              </svg>
                            {/if}
                          </span>
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="font-medium">Subtotal</Table.Cell>
                        <Table.Cell class="flex items-center gap-2">
                          <Input
                            type="number"
                            bind:value={formData.subtotal}
                            placeholder="N/A"
                            class="w-full"
                          />
                          <span>
                            {#if String(formData?.total).includes('$') || formData?.items?.[0]?.currency === 'USD'}
                              $
                            {:else}
                              <svg
                                class="w-[15px] fill-white"
                                xmlns="http://www.w3.org/2000/svg"
                                id="Layer_1"
                                data-name="Layer 1"
                                viewBox="0 0 1124.14 1256.39"
                              >
                                <path
                                  d="M699.62,1113.02h0c-20.06,44.48-33.32,92.75-38.4,143.37l424.51-90.24c20.06-44.47,33.31-92.75,38.4-143.37l-424.51,90.24Z"
                                />
                                <path
                                  d="M1085.73,895.8c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.33v-135.2l292.27-62.11c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.27V66.13c-50.67,28.45-95.67,66.32-132.25,110.99v403.35l-132.25,28.11V0c-50.67,28.44-95.67,66.32-132.25,110.99v525.69l-295.91,62.88c-20.06,44.47-33.33,92.75-38.42,143.37l334.33-71.05v170.26l-358.3,76.14c-20.06,44.47-33.32,92.75-38.4,143.37l375.04-79.7c30.53-6.35,56.77-24.4,73.83-49.24l68.78-101.97v-.02c7.14-10.55,11.3-23.27,11.3-36.97v-149.98l132.25-28.11v270.4l424.53-90.28Z"
                                />
                              </svg>
                            {/if}
                          </span>
                        </Table.Cell>
                      </Table.Row>

                      <Table.Row>
                        <Table.Cell class="text-xl font-medium">Total</Table.Cell>
                        <Table.Cell class="flex items-center gap-2 text-xl">
                          <Input
                            type="number"
                            bind:value={formData.total}
                            placeholder="N/A"
                            class="w-full"
                          />
                          <span>
                            {#if String(formData?.total).includes('$') || formData?.items?.[0]?.currency === 'USD'}
                              $
                            {:else}
                              <svg
                                class="w-[15px] fill-white"
                                xmlns="http://www.w3.org/2000/svg"
                                id="Layer_1"
                                data-name="Layer 1"
                                viewBox="0 0 1124.14 1256.39"
                              >
                                <path
                                  d="M699.62,1113.02h0c-20.06,44.48-33.32,92.75-38.4,143.37l424.51-90.24c20.06-44.47,33.31-92.75,38.4-143.37l-424.51,90.24Z"
                                />
                                <path
                                  d="M1085.73,895.8c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.33v-135.2l292.27-62.11c20.06-44.47,33.32-92.75,38.4-143.37l-330.68,70.27V66.13c-50.67,28.45-95.67,66.32-132.25,110.99v403.35l-132.25,28.11V0c-50.67,28.44-95.67,66.32-132.25,110.99v525.69l-295.91,62.88c-20.06,44.47-33.33,92.75-38.42,143.37l334.33-71.05v170.26l-358.3,76.14c-20.06,44.47-33.32,92.75-38.4,143.37l375.04-79.7c30.53-6.35,56.77-24.4,73.83-49.24l68.78-101.97v-.02c7.14-10.55,11.3-23.27,11.3-36.97v-149.98l132.25-28.11v270.4l424.53-90.28Z"
                                />
                              </svg>
                            {/if}
                          </span>
                        </Table.Cell>
                      </Table.Row>
                    </Table.Body>
                  </Table.Root>

                  <Separator />

                  <!-- Item Details Section -->
                  <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold">Item Details</h3>
                    <Button
                      type="button"
                      variant="outline"
                      on:click={() =>
                        (formData.items = [
                          ...formData.items,
                          {
                            description: '',
                            amount: '',
                            currency: 'SAR',
                            quantity: '',
                            warranty: {
                              hasWarranty: false,
                              periodMonths: 12,
                              expiryDate: undefined
                            }
                          }
                        ])}
                    >
                      Add Item
                    </Button>
                  </div>

                  <Table.Root>
                    <Table.Header>
                      <Table.Row>
                        <Table.Head>Item</Table.Head>
                        <Table.Head>Quantity</Table.Head>
                        <Table.Head>Currency</Table.Head>
                        <Table.Head>Amount</Table.Head>
                        <Table.Head>Warranty</Table.Head>
                        <Table.Head>Period</Table.Head>
                        <Table.Head>Actions</Table.Head>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {#if formData.items && formData.items.length > 0}
                        {#each formData.items as item, index}
                          <Table.Row>
                            <Table.Cell>
                              <Input type="text" bind:value={item.description} placeholder="N/A" />
                            </Table.Cell>
                            <Table.Cell>
                              <Input type="number" bind:value={item.quantity} placeholder="N/A" />
                            </Table.Cell>
                            <Table.Cell>
                              <Select.Root
                                selected={item.currency
                                  ? { value: item.currency, label: item.currency }
                                  : { value: 'SAR', label: 'SAR' }}
                                onSelectedChange={(selected) => {
                                  if (selected) {
                                    handleItemChange(index, 'currency', selected.value);
                                  }
                                }}
                              >
                                <Select.Trigger class="w-full">
                                  <Select.Value placeholder="Select currency" />
                                </Select.Trigger>
                                <Select.Content>
                                  <Select.Item value="SAR">SAR</Select.Item>
                                  <Select.Item value="USD">USD</Select.Item>
                                </Select.Content>
                              </Select.Root>
                            </Table.Cell>
                            <Table.Cell>
                              <Input type="number" bind:value={item.amount} placeholder="N/A" />
                            </Table.Cell>
                            <Table.Cell>
                              <Select.Root
                                selected={item.warranty
                                  ? {
                                      value: item.warranty.hasWarranty ? 'Yes' : 'No',
                                      label: item.warranty.hasWarranty ? 'Yes' : 'No'
                                    }
                                  : { value: 'No', label: 'No' }}
                                onSelectedChange={(selected) => {
                                  if (selected) {
                                    handleWarrantyChange(index, selected.value === 'Yes');
                                  }
                                }}
                              >
                                <Select.Trigger class="w-full">
                                  <Select.Value placeholder="Has warranty?" />
                                </Select.Trigger>
                                <Select.Content>
                                  <Select.Item value="Yes">Yes</Select.Item>
                                  <Select.Item value="No">No</Select.Item>
                                </Select.Content>
                              </Select.Root>
                            </Table.Cell>
                            <Table.Cell>
                              {#if item.warranty?.hasWarranty}
                                <Select.Root
                                  selected={item.warranty?.isCustomPeriodInDays
                                    ? { value: 'other', label: 'Custom (D)' }
                                    : item.warranty?.periodMonths !== undefined
                                      ? {
                                          value: item.warranty.periodMonths.toString(),
                                          label: `${item.warranty.periodMonths} months`
                                        }
                                      : { value: '12', label: '12 months' }}
                                  onSelectedChange={(selected) =>
                                    handlePeriodSelection(index, selected)}
                                >
                                  <Select.Trigger class="w-full">
                                    <Select.Value placeholder="Select Warranty Period" />
                                  </Select.Trigger>
                                  <Select.Content>
                                    <Select.Item value="3">3 months</Select.Item>
                                    <Select.Item value="6">6 months</Select.Item>
                                    <Select.Item value="12">12 months</Select.Item>
                                    <Select.Item value="24">24 months</Select.Item>
                                    <Select.Item value="36">36 months</Select.Item>
                                    <Select.Item value="other">Custom (D)</Select.Item>
                                  </Select.Content>
                                </Select.Root>
                              {:else}
                                <span class="text-muted-foreground">N/A</span>
                              {/if}
                            </Table.Cell>
                            <Table.Cell>
                              <Button
                                type="button"
                                variant="destructive"
                                size="sm"
                                on:click={() =>
                                  (formData.items = formData.items.filter(
                                    (_: any, i: number) => i !== index
                                  ))}
                              >
                                Remove
                              </Button>
                            </Table.Cell>
                          </Table.Row>
                        {/each}
                      {:else}
                        <Table.Row>
                          <Table.Cell colspan={7} class="text-center text-muted-foreground">
                            No items added. Use the "Add Item" button to add items.
                          </Table.Cell>
                        </Table.Row>
                      {/if}
                    </Table.Body>
                  </Table.Root>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-4 pt-4">
            <Dialog.Close>
              <Button type="button" variant="outline">Cancel</Button>
            </Dialog.Close>
            <Button type="submit">Save Changes</Button>
          </div>
        </form>
      </Dialog.Description>
    </Dialog.Content>
  </Dialog.Root>
</main>
