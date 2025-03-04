<script lang="ts">
  // Import shadcn components
  import { Button } from "./components/ui/button";
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card";
  import { Input } from "./components/ui/input";
  import { Label } from "./components/ui/label";
  import { Separator } from "./components/ui/separator";
  
  // Import a sample receipt data object instead of the JSON file that can't be found
  // Replace this with your actual data structure when available
  const receiptDataJson = {
    merchantName: { value: "Contoso Ltd.", confidence: 0.95 },
    date: { value: "2024-04-15", confidence: 0.98 },
    total: { value: "$125.40", confidence: 0.99 },
    category: { value: "Office Supplies", confidence: 0.90 },
    subtotal: { value: "$115.00", confidence: 0.97 },
    totalTax: { value: "$10.40", confidence: 0.96 }
  };

  // Define interfaces for receipt data
  export let receiptData = receiptDataJson;

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
      <Card>
        <CardHeader>
          <CardTitle>{receiptData?.merchantName?.value || 'Unknown'}</CardTitle>
          <CardDescription>{receiptData?.date?.value || 'No date'}</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="aspect-square w-full flex items-center justify-center rounded-md overflow-hidden bg-muted mb-4">
            <img 
              class="h-full w-full object-cover" 
              src="/src/assets/contoso-receipt.png" 
              alt="Receipt from {receiptData?.merchantName?.value || 'Unknown'}"
            />
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Category:</span>
              <span>{receiptData?.category?.value || 'N/A'}</span> 
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Subtotal:</span>
              <span>{receiptData?.subtotal?.value || 'N/A'}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Tax:</span>
              <span>{receiptData?.totalTax?.value || 'N/A'}</span>
            </div>
            <Separator />
            <div class="flex justify-between font-medium">
              <span>Total:</span>
              <span>{receiptData?.total?.value || 'N/A'}</span>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button  size="sm" class="w-full">View Details</Button>
        </CardFooter>
      </Card>

      <!-- Receipt 2 - using hardcoded sample data -->
      <Card>
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
      </Card>
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
