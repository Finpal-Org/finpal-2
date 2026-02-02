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
  import * as Select from './components/ui/select';
  import ChevronDown from 'lucide-svelte/icons/chevron-down';
  import type { ReceiptData } from '../../types';
  import contosoReceipt from '../../assets/contoso-receipt.png';

  // Tilt action for card hover effect
  function tilt(node: HTMLElement, options = { max: 15, scale: 1.03, speed: 300 }) {
    const handleMouseMove = (event: MouseEvent) => {
      const rect = node.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const tiltX = ((y - centerY) / centerY) * options.max * -1;
      const tiltY = ((x - centerX) / centerX) * options.max;

      node.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(${options.scale})`;
      node.style.transition = `transform 0ms ease-out`;
    };

    const handleMouseLeave = () => {
      node.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
      node.style.transition = `transform ${options.speed}ms ease-out`;
    };

    const handleMouseEnter = () => {
      node.style.transition = `transform ${options.speed}ms ease-out`;
    };

    node.addEventListener('mousemove', handleMouseMove);
    node.addEventListener('mouseleave', handleMouseLeave);
    node.addEventListener('mouseenter', handleMouseEnter);

    return {
      destroy() {
        node.removeEventListener('mousemove', handleMouseMove);
        node.removeEventListener('mouseleave', handleMouseLeave);
        node.removeEventListener('mouseenter', handleMouseEnter);
      }
    };
  }

  // Initialize loading state
  let isLoading = $state(false);
  // Track sort order
  let sortOrder = $state('newest');

  // Hardcoded dummy receipts for display
  const dummyReceipts: ReceiptData[] = [
    {
      receipt_id: 'dummy_001',
      category: 'Food & Dining',
      date: '2024-01-15',
      vendor: {
        name: 'Starbucks Coffee',
        address: '123 Main Street, Riyadh, Saudi Arabia',
        phone: '+966 11 123 4567'
      },
      line_items: [
        {
          id: 1,
          description: 'Grande Latte',
          quantity: 1,
          total: '25.00'
        },
        {
          id: 2,
          description: 'Blueberry Muffin',
          quantity: 1,
          total: '15.00'
        }
      ],
      subtotal: '40.00',
      tax: '6.00',
      total: '46.00',
      tip: '5.00',
      currency: 'SAR',
      payment: {
        type: 'Credit Card',
        display_name: 'Visa ****1234'
      },
      invoice_number: 'SB-2024-001234',
      note: 'Morning coffee meeting',
      imageUrl: contosoReceipt,
      merchantName: 'Starbucks Coffee',
      createdTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
    },
    {
      receipt_id: 'dummy_002',
      category: 'Shopping',
      date: '2024-01-12',
      vendor: {
        name: 'IKEA Saudi Arabia',
        address: '456 King Fahd Road, Jeddah, Saudi Arabia',
        phone: '+966 12 987 6543'
      },
      line_items: [
        {
          id: 1,
          description: 'Desk Chair',
          quantity: 1,
          total: '450.00'
        },
        {
          id: 2,
          description: 'Desk Lamp',
          quantity: 1,
          total: '120.00'
        },
        {
          id: 3,
          description: 'Storage Box Set',
          quantity: 2,
          total: '80.00'
        }
      ],
      subtotal: '650.00',
      tax: '97.50',
      total: '747.50',
      currency: 'SAR',
      payment: {
        type: 'Debit Card',
        display_name: 'Mastercard ****5678'
      },
      invoice_number: 'IKEA-2024-005678',
      note: 'Office furniture purchase',
      imageUrl: contosoReceipt,
      merchantName: 'IKEA Saudi Arabia',
      createdTime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
    },
    {
      receipt_id: 'dummy_003',
      category: 'Transportation',
      date: '2024-01-16',
      vendor: {
        name: 'Uber',
        address: 'Online Service',
        phone: '+966 800 123 4567'
      },
      line_items: [
        {
          id: 1,
          description: 'Ride from Airport to Hotel',
          quantity: 1,
          total: '85.50'
        }
      ],
      subtotal: '85.50',
      tax: '12.83',
      total: '98.33',
      tip: '10.00',
      currency: 'SAR',
      payment: {
        type: 'Credit Card',
        display_name: 'Visa ****9012'
      },
      invoice_number: 'UBER-2024-009012',
      note: 'Airport transfer',
      imageUrl: contosoReceipt,
      merchantName: 'Uber',
      createdTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
    }
  ];

  // Combine dummy receipts with fetched receipts and sort them
  let displayReceipts = $derived.by(() => {
    const allReceipts = [...dummyReceipts, ...receipts];

    // Sort by createdTime
    return [...allReceipts].sort((a, b) => {
      // If both have createdTime, compare normally
      if (a.createdTime && b.createdTime) {
        const dateA = a.createdTime instanceof Date ? a.createdTime : new Date(a.createdTime);
        const dateB = b.createdTime instanceof Date ? b.createdTime : new Date(b.createdTime);
        return sortOrder === 'newest'
          ? dateB.getTime() - dateA.getTime() // newest first
          : dateA.getTime() - dateB.getTime(); // oldest first
      }
      // If a has no createdTime, put it at the end
      if (!a.createdTime && b.createdTime) return 1;
      // If b has no createdTime, put it at the end
      if (a.createdTime && !b.createdTime) return -1;
      // If neither has createdTime, keep original order
      return 0;
    });
  });

  // Simple sort function to sort receipts by createdTime
  function sortReceipts() {
    // Sorting is now handled in the derived value
    // This function is kept for compatibility but doesn't need to do anything
  }

  // Toggle sort order
  function toggleSortOrder(order: string) {
    if (order !== sortOrder) {
      sortOrder = order;
      sortReceipts();
    }
  }

  onMount(async () => {
    try {
      isLoading = true;
      await getReceipts();
      // Sort according to current sort order
      sortReceipts();
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

    <!-- Sort buttons -->
    <div class="flex justify-end gap-2">
      <Button
        variant={sortOrder === 'newest' ? 'default' : 'outline'}
        size="sm"
        on:click={() => toggleSortOrder('newest')}
      >
        Newest First
      </Button>
      <Button
        variant={sortOrder === 'oldest' ? 'default' : 'outline'}
        size="sm"
        on:click={() => toggleSortOrder('oldest')}
      >
        Oldest First
      </Button>
    </div>

    <div class="grid gap-6">
      <Separator />
      <!-- (auto-fit) stacks receipt in the row infinitly if there is space (350px each receipt) -->
      <div class="grid auto-rows-fr grid-cols-[repeat(auto-fit,minmax(350px,1fr))] gap-10">
        <!-- Loading msgs -->
        {#if isLoading}
          <h1>Loading...</h1>
        {:else if displayReceipts.length === 0}
          <h1>No receipts Found.. Please Upload a Receipt</h1>

          <!-- if there are receipts fetch them all-->
        {:else}
          <!-- Loop over receipts -->
          {#each displayReceipts as receipt (receipt.receipt_id)}
            <div class="flex justify-center">
              <!-- TODO: Animation doesnt work after uploading.. only on mount-->
              <div use:tilt={{ max: 2, scale: 1.02, speed: 400 }} class="h-full w-full">
                <Card
                  class="receipt-card my-3 grid h-full w-full grid-rows-[auto_1fr_auto] duration-500 animate-in fade-in"
                >
                  <CardHeader class="flex flex-row justify-between gap-5">
                    <div class="flex flex-col gap-2">
                      <CardTitle>
                        {receipt.vendor?.name || receipt.merchantName || 'Merchant'}
                      </CardTitle>
                      <CardDescription>{receipt?.category || 'Other'}</CardDescription>
                    </div>
                    <div class="flex">
                      <ReceiptEdit {receipt} />
                    </div>
                  </CardHeader>

                  <!-- the Card Content -->
                  <ReceiptCardContent {receipt} />
                  <!-- todo i need the footer to be at very bottom of card  -->
                  <CardFooter>
                    <!-- TODO: Onclick Expand or popup Detailed view -->
                    <ReceiptDetails {receipt} />
                  </CardFooter>
                </Card>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
  .receipt-card {
    transition:
      transform 400ms ease-out,
      box-shadow 400ms ease-out;
    will-change: transform;
    transform-style: preserve-3d;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .receipt-card:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
</style>
