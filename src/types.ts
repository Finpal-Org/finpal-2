// export interface ReceiptField {
//   value: string;
//   confidence: number;
// }
// todo flattened, this is inside the receipt field

export interface ReceiptData {
  id?: string;
  merchantName?: string;
  phone?: string;
  date?: string;
  time?: string;
  total?: string;
  image?: string;
  category?: string;
  taxDetails?: string;
  totalTax?: string;
  subtotal?: string;
  items?: {
    description: string;
    amount: string;
    currency: string;
    quantity: string;
  }[];
  address?: string;
}
