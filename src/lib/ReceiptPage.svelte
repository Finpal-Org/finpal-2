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

  // Simple sort function to sort receipts by createdTime
  function sortReceipts() {
    if (!receipts || receipts.length === 0) return;

    receipts.sort((a, b) => {
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
        {:else if receipts.length === 0}
          <h1>No receipts Found.. Please Upload a Receipt</h1>

          <!-- if there are receipts fetch them all-->
        {:else}
          <!-- Loop over receipts -->
          {#each receipts as receipt (receipt.receipt_id)}
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
