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
  // Core fields matching the iOS structure
  id?: string;
  receipt_id?: string;
  receipt_image?: string;
  category?: string;
  date?: string;
  invoice_number?: string;
  is_duplicate?: boolean;
  note?: string;

  // Line items
  line_items?: {
    id?: string | number;
    description?: string;
    quantity?: number | string;
    total?: number | string;
  }[];

  // Payment
  payment?: {
    display_name?: string;
    type?: string;
  };

  // Vendor
  vendor?: {
    logo?: string;
    name?: string;
    address?: string;
    phone?: string;
  };

  // Financial details
  subtotal?: number | string;
  tax?: number | string;
  total?: number | string;
  tip?: string;
  currency?: string;

  // Internal fields
  user_id?: string;
  createdTime?: Date;
  imageUrl?: string;

  // Legacy fields for backward compatibility
  merchantName?: string;
  address?: string;
  phone?: string;
  totalTax?: string;
  transactionId?: string;
  items?: any[];
}
