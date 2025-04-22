<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Label } from './ui/label';
  import { Input } from './ui/input';
  import { Button } from './ui/button';
  import type { ReceiptData } from '../../types';
  import { Separator } from './ui/separator';
  import * as Select from './ui/select/index';
  import { standardCategories } from '../utils/categoryMapping';
  import { calculateWarrantyExpiry, monthsToDays } from '../utils/warrantyUtils';
  import { createEventDispatcher } from 'svelte';
  import type { Selected } from 'bits-ui';

  // Define props with proper typing
  interface $$Props {
    receipt: ReceiptData;
  }

  // Use $props() for Svelte 5 runes
  const receipt = $props();

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

  //todo remove? // Handle currency selection
  // function handleCurrencyChange(index: number, value: string) {
  //   handleItemChange(index, 'currency', value);
  // }

  // todo remove?// Handle category selection
  // function handleCategoryChange(value: string) {
  //   formData.category = value;
  // }

  // todo remove? // Handle period selection
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
          <!-- todo cancel doesnt exit edit dialog -->
          <Button variant="outline" on:click={cancelCustomDays}>Cancel</Button>
          <Button on:click={saveCustomDays}>Save</Button>
        </Dialog.Footer>
      </Dialog.Content>
    </Dialog.Root>
  {/if}

  <Dialog.Root>
    <!--todo  make edit button bigger & easier to click -->
    <Dialog.Trigger
      ><Button size="lg" variant="secondary" class="w-full text-green-500">Edit</Button
      ></Dialog.Trigger
    >
    <Dialog.Content class="max-w-6xl">
      <Dialog.Header>
        <Dialog.Title>Edit Receipt</Dialog.Title>
        <Dialog.Description>
          <form on:submit={handleSubmit} class="space-y-6">
            <!-- Basic Information -->
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <Label>Merchant Name</Label>
                <Input
                  type="text"
                  name="merchantName"
                  bind:value={formData.merchantName}
                  placeholder="Merchant Name"
                />
              </div>
              <div class="flex flex-col gap-2">
                <Label>Category</Label>
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
                    <Select.Value placeholder="Select a category" />
                  </Select.Trigger>
                  <Select.Content>
                    {#each standardCategories as category}
                      <Select.Item value={category} label={category}>{category}</Select.Item>
                    {/each}
                  </Select.Content>
                </Select.Root>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <Label>Phone</Label>
                <Input
                  type="tel"
                  name="phone"
                  bind:value={formData.phone}
                  placeholder="Phone Number"
                />
              </div>
              <div class="flex flex-col gap-2">
                <Label>Address</Label>
                <Input
                  type="text"
                  name="address"
                  bind:value={formData.address}
                  placeholder="Address"
                />
              </div>
            </div>

            <!-- Date and Time -->
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <Label>Date</Label>
                <Input type="date" name="date" bind:value={formData.date} />
              </div>
              <div class="flex flex-col gap-2">
                <Label>Time</Label>
                <Input type="time" name="time" bind:value={formData.time} />
              </div>
            </div>

            <!-- Financial Information -->
            <div class="grid grid-cols-3 gap-4">
              <div class="flex flex-col gap-2">
                <Label>Subtotal</Label>
                <Input
                  type="number"
                  name="subtotal"
                  bind:value={formData.subtotal}
                  placeholder="0.00"
                />
              </div>
              <div class="flex flex-col gap-2">
                <Label>VAT Total</Label>
                <Input
                  type="number"
                  name="totalTax"
                  bind:value={formData.totalTax}
                  placeholder="0.00"
                />
              </div>
              <div class="flex flex-col gap-2">
                <Label>Total</Label>
                <Input type="number" name="total" bind:value={formData.total} placeholder="0.00" />
              </div>
            </div>

            <Separator />

            <!-- Items -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">Items</h3>
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
                        warranty: { hasWarranty: false, periodMonths: 12, expiryDate: undefined }
                      }
                    ])}
                >
                  Add Item
                </Button>
              </div>

              {#each formData.items as item, index}
                <div class="grid grid-cols-4 gap-4 rounded-lg border p-4">
                  <div class="flex flex-col gap-2">
                    <Label>Description</Label>
                    <Input
                      type="text"
                      bind:value={item.description}
                      placeholder="Item description"
                    />
                  </div>
                  <div class="flex flex-col gap-2">
                    <Label>Quantity</Label>
                    <Input type="number" bind:value={item.quantity} placeholder="1" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <Label>Amount</Label>
                    <Input type="number" bind:value={item.amount} placeholder="0.00" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <Label>Currency</Label>
                    <Select.Root
                      selected={item.currency
                        ? { value: item.currency, label: item.currency }
                        : undefined}
                      onSelectedChange={(selected) => {
                        if (selected) {
                          handleItemChange(index, 'currency', selected.value);
                        }
                      }}
                    >
                      <Select.Trigger>
                        <Select.Value placeholder="Select currency" />
                      </Select.Trigger>
                      <Select.Content>
                        <Select.Item value="SAR">SAR</Select.Item>
                        <Select.Item value="USD">USD</Select.Item>
                      </Select.Content>
                    </Select.Root>
                  </div>
                  <div class="flex flex-col gap-2">
                    <Label>Warranty</Label>
                    <Select.Root
                      selected={item.warranty
                        ? {
                            value: item.warranty.hasWarranty ? 'Yes' : 'No',
                            label: item.warranty.hasWarranty ? 'Yes' : 'No'
                          }
                        : undefined}
                      onSelectedChange={(selected) => {
                        if (selected) {
                          handleWarrantyChange(index, selected.value === 'Yes');
                        }
                      }}
                    >
                      <Select.Trigger>
                        <Select.Value placeholder="Has warranty?" />
                      </Select.Trigger>
                      <Select.Content>
                        <Select.Item value="Yes">Yes</Select.Item>
                        <Select.Item value="No">No</Select.Item>
                      </Select.Content>
                    </Select.Root>
                  </div>

                  {#if item.warranty?.hasWarranty}
                    <div class="flex flex-col gap-2">
                      <Label>Warranty Period</Label>
                      <Select.Root
                        selected={item.warranty?.isCustomPeriodInDays
                          ? { value: 'other', label: 'Custom (D)' }
                          : item.warranty?.periodMonths !== undefined
                            ? {
                                value: item.warranty.periodMonths.toString(),
                                label: `${item.warranty.periodMonths} months`
                              }
                            : undefined}
                        onSelectedChange={(selected) => handlePeriodSelection(index, selected)}
                      >
                        <Select.Trigger class="w-48">
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
                    </div>
                  {/if}

                  {#if item.warranty?.hasWarranty && item.warranty?.periodMonths === 'other'}
                    <!-- Custom days input now handled by dialog -->
                  {/if}

                  <Button
                    type="button"
                    variant="destructive"
                    class="col-span-4"
                    on:click={() =>
                      (formData.items = formData.items.filter((_: any, i: number) => i !== index))}
                  >
                    Remove Item
                  </Button>
                </div>
              {/each}
            </div>

            <div class="flex justify-end gap-4">
              <Button type="button" variant="outline">Cancel</Button>
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </Dialog.Description>
      </Dialog.Header>
    </Dialog.Content>
  </Dialog.Root>
</main>
