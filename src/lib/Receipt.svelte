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
        <div  class="max-w-[350px]">
        <Card>  
          <CardHeader>
            <CardTitle>{receipt.merchantName ? receipt.merchantName : 'Unknown'}</CardTitle>
            <CardDescription>{receipt?.category || 'No date'}</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
              <img
                class="h-full w-full object-cover"
                src="/src/assets/contoso-receipt.png"
                alt=""
              />
            </div>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Category:</span>
                <span>{receipt?.category || 'N/A'}</span>
              </div>
              <!-- todo move address inside details  -->
              <div class="flex justify-between ">
                <span class="text-muted-foreground">Address:</span>
                <span class="font-size-sm">{receipt?.address|| 'N/A'}</span>
              </div>
        
              <div class="flex justify-between">
                <span class="text-muted-foreground">Subtotal:</span>
                <span>{receipt?.subtotal || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Tax:</span>
                <span>{receipt?.totalTax || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <!-- add arrow down icon and show items -->
                <span class="text-muted-foreground">More Details</span>
                <span class="text-muted-foreground">{"->"}</span>
              </div>
              <Separator />
              <div class="flex justify-between font-medium">
                <span>Total:</span>
                <span>{receipt?.total || 'N/A'}</span>
              </div>
        
            </div>
          </CardContent>
          <CardFooter>
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
