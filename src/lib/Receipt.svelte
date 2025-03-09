<script lang="ts">
 // Import shadcn components
 import { Button } from "./components/ui/button";
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card";
  import { Input } from "./components/ui/input";
  import { Label } from "./components/ui/label";
  import { Separator } from "./components/ui/separator";
  import { getReceipts, receipts} from "../../firebase/fireStore.svelte"
  import { onMount } from "svelte";

  let isLoading = $state(false);

  onMount(async ()=>{
    // on mount, wait to get receipts
    try{
      isLoading = true;
      await getReceipts()


    }catch(err){
      console.error(err)

    }finally{
       isLoading = false;
    }
  })

  // Define interfaces for receipt data
  // export let receiptData = receiptDataJson;


  // Create a sample receipt for the second card
  const sampleReceipt = {
    merchantName: { value: "Store Name", confidence: 0.9 },
    date: { value: "2024-03-15", confidence: 0.9 },
    total: { value: "$150.00", confidence: 0.9 },
    category: { value: "Groceries", confidence: 0.9 }
  };

</script>
<main>
<div class="container mx-auto p-6 space-y-8">
  <div class="flex flex-col space-y-2">
    <h1 class="text-3xl font-bold">Receipts</h1>
    <p class="text-muted-foreground">Upload and manage your receipts</p>
  </div>
  
  <div class="grid gap-6">
    <div class="flex items-center gap-4">
      <Label for="upload-file" class="sr-only">Upload Receipt</Label>
      <Input
        type="file"
        id="upload-file"
        accept=".pdf,.jpg,.jpeg,.png"
      />
      <Button variant="outline">Upload Receipt</Button>
    </div>
    
    <Separator />
    
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
       <!-- if Fetching receipts -->
      {#if isLoading}
        <h1>Loading...</h1>
      <!-- if there are no receipts -->
      {:else if receipts.length ===0}
        <h1>No receipts Found.. Please Upload a Receipt</h1>
      <!-- if there are receipts fetch em all-->
      {:else} 
        <!-- Loop over receipts -->
         {#each receipts as receipt }
        <div class="flex justify-center" >
        <Card class="max-w-[300px]">  
          <CardHeader>
            <CardTitle>{receipt.merchantName ? receipt.merchantName : 'Merchant'}</CardTitle>
            <CardDescription>{receipt?.category || 'Other'}</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
              <!-- TODO: onclick img expand & show retake option -->
              <img
                class="h-full w-full object-cover"
                src="/src/assets/contoso-receipt.png"
                alt=""
              />
            </div>
            <div class="space-y-2">
              <div class="flex gap-2 justify-between">
                <span class="text-muted-foreground">Category</span>
                <span>{receipt?.category || 'N/A'}</span>
              </div>
              <!-- todo move address inside details  -->
              <div class="flex gap-2 justify-between">
                <span class="text-muted-foreground">Date</span>
                <span class="font-size-sm">{receipt?.date|| 'N/A'}</span>
              </div>
        
              <div class="flex gap-2 justify-between">
                <span class="text-muted-foreground">Contact</span> 
                <!-- TODO: needs proper phone formating for quick access (copy paste) -->
                <span><a href="tel:{receipt?.phone || 'N/A'}"> {receipt?.phone || 'N/A'}</a></span>
              </div>
              <div class="flex gap-2 justify-between">
                <!-- PAYMENT METHOD TODO: -->
                <span class="text-muted-foreground">Vat Total</span>
                <!-- make riyal curr conditional: if currency is SA || empty , otherwise give dollar sign -->
                <span class="flex gap-1">{receipt?.totalTax || 'N/A'} <img class="w-[15px]" src="./saudi-riyal.svg" alt=""> </span>
              </div>
              <div class="flex gap-2 justify-between">
                <!-- PAYMENT METHOD TODO: -->
                <span class="text-muted-foreground">Payment Method</span>
                <span>{'Card'}</span>
              </div>
              <div class="flex justify-center">
                <span class="text-muted-foreground flex justify-center items-center "> 
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
          <CardFooter>
         <!-- TODO: Onclick Expand or popup Detailed view -->
            <Button  size="sm" class="w-full">View Details</Button>
          </CardFooter>
        </Card>
        </div>
        {/each}
      {/if}

      <!-- Receipt 2 - using hardcoded sample data -->
      <!-- <Card>
        <CardHeader>
          <CardTitle>{sampleReceipt.merchantName.value}</CardTitle>
          <CardDescription>{sampleReceipt.date.value}</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
            <span class="text-muted-foreground">Receipt Image</span>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Category:</span>
              <span>{sampleReceipt.category.value}</span>
            </div>
            <Separator />
            <div class="flex justify-between font-medium">
              <span>Total:</span>
              <span>{sampleReceipt.total.value}</span>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button  size="lg" class="w-full">View Details</Button>
        </CardFooter>
      </Card> -->
    </div>
  </div>
</div>
</main>
<style>
  /* You can add component-specific styles here if needed */
  /* #receipt-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  } */
</style>
