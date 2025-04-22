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
