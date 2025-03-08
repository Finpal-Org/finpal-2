export interface ReceiptField {
  value: string;
  confidence: number;
}

export interface ReceiptData {
  id?: string;
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
  address?: ReceiptField;
}
