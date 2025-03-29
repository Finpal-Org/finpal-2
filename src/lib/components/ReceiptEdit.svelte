<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Label } from './ui/label';
  import { Input } from './ui/input';
  import { Button } from './ui/button';
  import type { ReceiptData } from '../../types';
  import { Separator } from './ui/separator';
  import * as Select from './ui/select/index';

  // Define props with proper typing
  interface $$Props {
    receipt: ReceiptData;
  }

  // Use $props() for Svelte 5 runes
  const receipt = $props();

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
        quantity: ''
      };
    }
    formData.items[index][field] = value;
  }

  // Handle currency selection
  function handleCurrencyChange(index: number, value: string) {
    handleItemChange(index, 'currency', value);
  }
</script>

<main>
  <Dialog.Root>
    <Dialog.Trigger><Button variant="secondary" class="text-green-500">Edit</Button></Dialog.Trigger
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
                <Input
                  type="text"
                  name="category"
                  bind:value={formData.category}
                  placeholder="Category"
                />
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
                      { description: '', amount: '', currency: 'SAR', quantity: '' }
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
                    <Select.Root>
                      <Select.Trigger>
                        <Select.Value placeholder={item.currency || 'Select currency'} />
                      </Select.Trigger>
                      <Select.Content>
                        <Select.Item value="SAR">SAR</Select.Item>
                        <Select.Item value="USD">USD</Select.Item>
                      </Select.Content>
                    </Select.Root>
                  </div>
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
