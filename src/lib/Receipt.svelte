<script lang="ts">
  // Import shadcn components
  import { Button } from "./components/ui/button";
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card";
  import { Input } from "./components/ui/input";
  import { Label } from "./components/ui/label";
  import { Separator } from "./components/ui/separator";
  import { getReceipts, receiptFields} from "../../firebase/fireStore.svelte"
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

  // receiptFields;
  // call getReceipts to update *receiptFields* data 
  // const getReceiptPage = async ()=>{
  //   await getReceipts()
  // }
 
  // getReceiptPage()

  // Define interfaces for receipt data
  // export let receiptData = receiptDataJson;

  interface ReceiptField {
    value: string;
    confidence: number;
  }
  
  interface ReceiptData {
    merchantName?: ReceiptField;
    phone?: ReceiptField;
    date?: ReceiptField;
    time?: ReceiptField;
    total?: ReceiptField;
    image?: ReceiptField;
    category?: ReceiptField;
    taxDetails?: ReceiptField;
    totalTax?: ReceiptField;
    subtotal?: ReceiptField;
    items?: ReceiptField;
  }

  // Create a sample receipt for the second card
  const sampleReceipt = {
    merchantName: { value: "Store Name", confidence: 0.9 },
    date: { value: "2024-03-15", confidence: 0.9 },
    total: { value: "$150.00", confidence: 0.9 },
    category: { value: "Groceries", confidence: 0.9 }
  };

  // Function to handle file upload
  function handleFileUpload(event: Event): void {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      console.log("File uploaded:", file.name);
      // Here you would process the file, perhaps send it to an API
      // For now we just log it
    }
  }
</script>

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
        on:change={handleFileUpload}
      />
      <Button variant="outline">Upload Receipt</Button>
    </div>
    
    <Separator />
    
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <!-- Receipt 1 - using data from receiptData -->
      {#if isLoading}
      <h1>Loading...</h1>
      {:else}
      <Card>
        <CardHeader>
          <CardTitle>{receiptFields?.merchantName || 'Unknown'}</CardTitle>
          <CardDescription>{receiptFields?.date || 'No date'}</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
            <img 
              class="h-full w-full object-cover" 
              src="/src/assets/contoso-receipt.png" 
              alt="Receipt from {receiptFields?.merchantName || 'Unknown'}"
            />
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Category:</span>
              <span>{receiptFields?.category || 'N/A'}</span> 
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Address:</span>
              <span>{receiptFields?.address || 'N/A'}</span> 
            </div>
            
            <div class="flex justify-between">
              <span class="text-muted-foreground">Subtotal:</span>
              <span>{receiptFields?.subtotal || 'N/A'}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Tax:</span>
              <span>{receiptFields?.totalTax || 'N/A'}</span>
            </div>
            <div class="flex justify-between">
              <!-- add arrow down icon and show items -->
              <span class="text-muted-foreground">More Details</span>
              <span class="text-muted-foreground">{"->"}</span>

            </div>

            <Separator />

            <div class="flex justify-between font-medium">
              <span>Total:</span>
              <span>{receiptFields?.total || 'N/A'}</span>
            </div>
           
          </div>
        </CardContent>
        <CardFooter>
          <Button  size="sm" class="w-full">View Details</Button>
        </CardFooter>
      </Card>
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

<style>
  /* You can add component-specific styles here if needed */
  /* #receipt-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  } */
</style>
