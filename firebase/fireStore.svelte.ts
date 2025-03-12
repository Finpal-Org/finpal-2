import { collection, getDocs, orderBy, query } from 'firebase/firestore';
import { db } from './firebaseConfig';
import type { ReceiptData } from '../src/types';
// import type ReceiptField from '../src/lib/Receipt.svelte';

export let receipts: ReceiptData[] = $state([]); // init reactive receipts as empty array

const receiptCollection = collection(db, 'receipts'); //receipt collection ref

export async function getReceipts() {
  //fetch receipts from firestore
  try {
    //1. before getting docs lets order them by create date (newest first)
    const receiptsQuery = query(receiptCollection, orderBy('createdTime', 'desc')); //query collection, filter by order decending
    const receiptDocs = await getDocs(receiptsQuery); //fetch filtered receipts docs

    //2.Loop over Receipts and store them in receipts array

    receipts.length = 0;

    receiptDocs.docs.forEach((doc) => {
      // Extract all the data first
      const rawData = doc.data();

      interface item {
        Description: string;
        Amount: string;
        Currency: string;
        Quantity: string;
      }

      // item empty bu default
      let itemsProperties = [];

      // if there are items
      if (rawData && rawData.items) {
        //if there are items nested
        if (rawData && rawData.items && rawData.items.content) {
          itemsProperties = rawData.items.content.map((item: item) => ({
            description: item.Description || '',
            amount: item.Amount || '',
            currency: item.Currency || 'SAR',
            quantity: item.Quantity || ''
          }));
          // else items flat
        } else {
          itemsProperties = rawData.items.map((item: item) => ({
            description: item.Description || '',
            amount: item.Amount || '',
            currency: item.Currency || 'SAR',
            quantity: item.Quantity || ''
          }));
        }
      }
      // rawData && rawData.items ?

      // : rawData.items.content.map((item: item) => {
      //     return {
      //       description: item.Description || '',
      //       amount: item.Amount || '',
      //       currency: item.Currency || 'SAR',
      //       quantity: item.Quantity || ''
      //     };
      //   });

      //Step 1 Flattened version:

      // STEP 1: Create separate variables with explicit checks
      // const merchantContent =
      //   // if rawData.merchantName exists, then get the content
      //   rawData && rawData.merchantName && rawData.merchantName.content
      //     ? rawData.merchantName.content
      //     : 'Unknown';

      // const addressContent =
      //   rawData && rawData.address && rawData.address.content ? rawData.address.content : 'Unknown';

      // const categoryContent =
      //   rawData && rawData.category && rawData.category.content
      //     ? rawData.category.content
      //     : 'Other';

      // const dateContent =
      //   rawData && rawData.date && rawData.date.content ? rawData.date.content : 'Unknown';

      // const subtotalContent =
      //   rawData && rawData.subtotal && rawData.subtotal.content
      //     ? rawData.subtotal.content
      //     : 'Unknown';

      // const totalContent =
      //   rawData && rawData.total && rawData.total.content ? rawData.total.content : 'Unknown';

      // const totalTaxContent =
      //   rawData && rawData.totalTax && rawData.totalTax.content
      //     ? rawData.totalTax.content
      //     : 'Unknown';

      // // check if there is data-> there  is phone obj ->content of phone ?
      // const phoneContent =
      //   rawData && rawData.phone && rawData.phone.content ? rawData.phone.content : 'Unknown';

      // STEP 2: Build object from safe variables
      const safeReceipt = {
        id: doc.id, //TODO: do we need doc id?
        merchantName: rawData.merchantName || 'Unknown',
        address: rawData.address || 'Unknown',
        category: rawData.category || 'Other',
        date: rawData.date || 'Unknown',
        subtotal: rawData.subtotal || 'Unknown',
        total: rawData.total || 'Unknown',
        totalTax: rawData.totalTax || 'Unknown',
        phone: rawData.phone || 'Unknown',
        items: itemsProperties || 'Unknown'
      };

      receipts.push(safeReceipt);
    });
  } catch (err) {
    console.log(err, 'receipt fetch failed');
  }
}

//return/call getReceipt

// export const oneReceipt = getReceipt(receiptRef);
