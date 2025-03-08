import { collection, getDocs } from 'firebase/firestore';
import { db } from './firebaseConfig';
import type { ReceiptData } from '../src/types';
// import type ReceiptField from '../src/lib/Receipt.svelte';

export let receipts: ReceiptData[] = $state([]); // init receipts as empty array

const receiptCollection = collection(db, 'receipts'); //receipt collection ref

export async function getReceipts() {
  //fetch receipts from firestore
  try {
    const receiptDocs = await getDocs(receiptCollection); //1. fetch receipts docs

    //2.Loop over Receipts and store them in receipts array

    receipts.length = 0;

    receiptDocs.docs.forEach((doc) => {
      // Extract all the data first
      const rawData = doc.data();

      // STEP 1: Create separate variables with explicit checks
      const merchantContent =
        rawData && rawData.merchantName && rawData.merchantName.content
          ? rawData.merchantName.content
          : 'Unknown';

      const addressContent =
        rawData && rawData.address && rawData.address.content
          ? rawData.address.content
          : 'Unknown';

      const categoryContent =
        rawData && rawData.category && rawData.category.content
          ? rawData.category.content
          : 'Unknown';

      const dateContent =
        rawData && rawData.date && rawData.date.content
          ? rawData.date.content
          : 'Unknown';

      const subtotalContent =
        rawData && rawData.subtotal && rawData.subtotal.content
          ? rawData.subtotal.content
          : 'Unknown';

      const totalContent =
        rawData && rawData.total && rawData.total.content
          ? rawData.total.content
          : 'Unknown';

      const totalTaxContent =
        rawData && rawData.totalTax && rawData.totalTax.content
          ? rawData.totalTax.content
          : 'Unknown';

      // STEP 2: Build object from safe variables
      const safeReceipt = {
        id: doc.id,
        merchantName: merchantContent,
        address: addressContent,
        category: categoryContent,
        date: dateContent,
        subtotal: subtotalContent,
        total: totalContent,
        totalTax: totalTaxContent,
      };

      receipts.push(safeReceipt);
    });
  } catch (err) {
    console.log(err, 'receipt fetch failed');
  }
}

//return/call getReceipt

// export const oneReceipt = getReceipt(receiptRef);
