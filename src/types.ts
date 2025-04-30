// export interface ReceiptField {
//   value: string;
//   confidence: number;
// }
// flattened, this is inside the receipt field

//todo add all possible fields
// CountryRegion
// Payments
// TaxDetails.*.Rate
// TaxDetails.*.Description

export interface ReceiptData {
  id?: string;
  merchantName?: string;
  phone?: string;
  date?: string;
  time?: string;
  total?: string;
  image?: string;
  imageUrl?: string; // URL to the receipt image in Firebase Storage
  category?: string;
  taxDetails?: string; // TaxDetails as a simple string
  totalTax?: string;
  subtotal?: string;
  countryRegion?: string; // Country where the receipt was issued

  //todo the ios receipt data:
  /*
  receipt_id: "541E7A42-1771-4AB0-A1E2-A6F295936145"
receipt_image: https://firebasestorage.googleapis.com/...
category: "Meal"
date: March 30, 2025 at 7:10:22AM
invoice_number: "123456"
is_duplicate: false
note: "Hello World..."

line_items:
    0:
        id: 12345678
        description: "Pizza"
        quantity: 2
        total: 45.43
    1:
        id: 123456789
        description: "Water"
        quantity: 1
        total: 2.43

payment:
    display_name: "Mada"
    type: "mada"

vendor:
    logo: https://firebasestorage.googleapis.com/...
    name: "Pizza Hut"

subtotal: 77.39
tax: 11.45
total: 88.84
user_id: "n0XUczKL7SVy6MJfHearCUFsDeQ2"
*/

  // Flattened tax details (from first tax item for easy access)
  taxRate?: string;
  taxDescription?: string;
  taxNetAmount?: string;

  // Structured tax details with rate, description and netAmount
  taxDetailsArray?: {
    rate?: string;
    description?: string;
    netAmount?: string;
  }[];

  // todo correct? Payment field can come in different formats based on Azure API response

  payment?: {
    method?: string;
    amount?: string;
    type?: string; // Alternative field name
  };
  items?: {
    description: string;
    amount: string;
    currency: string;
    quantity: string;
    warranty?: {
      hasWarranty: boolean;
      periodMonths: number | 'other';
      expiryDate?: string;
      isCustomPeriodInDays?: boolean;
    };
  }[];
  address?: string;
  createdTime?: Date;
  tip?: string; // Amount of tip included
  currency?: string; // Currency used in the receipt
}
