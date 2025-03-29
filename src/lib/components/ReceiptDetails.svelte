<script lang="ts">
  import * as Dialog from './ui/dialog/index';
  import { Button } from './ui/button';
  import Input from './ui/input/input.svelte';
  import Label from './ui/label/label.svelte';
  import * as Select from './ui/select/index';
  import type { ReceiptData } from '../../types';
  import ReceiptCardContent from './ReceiptCardContent.svelte';
  import CardContent from './ui/card/card-content.svelte';
  import Separator from './ui/separator/separator.svelte';
  import * as Table from './ui/table/index';

  // Add receipt prop
  export let receipt: ReceiptData;
</script>

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
                    <Table.Row>
                      <Table.Cell class="font-medium">Category</Table.Cell>
                      <Table.Cell>{receipt?.category || 'N/A'}</Table.Cell>
                    </Table.Row>
                    <Table.Row>
                      <Table.Cell class="font-medium">Date</Table.Cell>
                      <Table.Cell>{receipt?.date || 'N/A'}</Table.Cell>
                    </Table.Row>
                    <Table.Row>
                      <Table.Cell class="font-medium">Contact</Table.Cell>
                      <Table.Cell
                        ><a href="tel:{receipt?.phone || 'N/A'}">
                          {receipt?.phone || 'N/A'}</a
                        ></Table.Cell
                      >
                    </Table.Row>
                    <Table.Row>
                      <Table.Cell class="font-medium">VAT Total</Table.Cell>
                      <Table.Cell class="flex items-center gap-2">
                        {receipt?.totalTax || 'N/A'}
                        <span>
                          {#if receipt?.totalTax?.includes('USD')}
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
                    <Table.Row>
                      <Table.Cell class="font-medium">Payment Method</Table.Cell>
                      <Table.Cell>Card</Table.Cell>
                    </Table.Row>
                    <Table.Row>
                      <Table.Cell class="text-xl font-medium">Total</Table.Cell>
                      <Table.Cell class="flex items-center gap-2 text-xl">
                        {receipt?.total || 'N/A'}
                        <span>
                          {#if receipt?.total?.includes('USD')}
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
                      <Table.Head>Image</Table.Head>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                    {#if receipt.items}
                      {#each receipt.items as item}
                        <Table.Row>
                          <Table.Cell>{item?.description || 'unknown'}</Table.Cell>
                          <Table.Cell>{item?.quantity || 'unknown'}</Table.Cell>
                          <!-- todo receipt currency != item currency -->
                          <Table.Cell class="text-center">
                            {#if item?.currency === 'USD'}
                              $
                            {:else if item?.currency === 'SAR'}
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
                            {:else}
                              {item?.currency || 'unknown'}
                            {/if}
                          </Table.Cell>
                          <Table.Cell>{item?.quantity || 'unknown'}</Table.Cell>
                          <Table.Cell
                            ><Select.Root>
                              <Select.Trigger>
                                <Select.Value placeholder="Has Warranty">No</Select.Value>
                              </Select.Trigger>
                              <Select.Content>
                                <Select.Item value="yes">Yes</Select.Item>
                                <Select.Item value="no">No</Select.Item>
                              </Select.Content>
                            </Select.Root>
                          </Table.Cell>
                          <Table.Cell>
                            <Select.Root>
                              <Select.Trigger>
                                <Select.Value placeholder="Select Period">12 months</Select.Value>
                              </Select.Trigger>
                              <Select.Content>
                                <Select.Item value="12">12 months</Select.Item>
                                <Select.Item value="24">24 months</Select.Item>
                                <Select.Item value="other">Other</Select.Item>
                                <!-- TODO add input for other period -->
                                <!-- {#if Select.Content.value === 'other'}
                                  <Input type="text" placeholder="type period" />
                                {/if} -->
                              </Select.Content>
                            </Select.Root>
                          </Table.Cell>
                          <Table.Cell>
                            <Input type="file" />
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
