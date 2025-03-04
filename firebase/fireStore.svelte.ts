import { collection, getDocs } from 'firebase/firestore';
import { db } from './firebaseConfig';
import { writable } from 'svelte/store';

const receiptCollection = collection(db, 'receipts');

// export let receiptFields = writable({
//   // placeholder values
//   merchantName: 'test-merchant',
//   address: 'test-address',
//   category: 'test-category',
//   date: 'test-date',
//   subtotal: 'test-subtotal',
//   total: 'test-total',
//   totalTax: 'test-totalTax',
// });
export let receiptFields = $state({
  // placeholder values
  merchantName: 'test-merchant',
  address: 'test-address',
  category: 'test-category',
  date: 'test-date',
  subtotal: 'test-subtotal',
  total: 'test-total',
  totalTax: 'test-totalTax',
});

export async function getReceipts() {
  try {
    //1. fetch receipts docs
    const getReceiptDocs = await getDocs(receiptCollection);

    //2.loop over docs (fields) and log them
    getReceiptDocs.forEach((doc) => {
      // console.log("ID: ", doc.id);
      console.log('Address: ', doc.data().address.content);
      console.log('Category: ', doc.data().category.content);
      console.log('Date: ', doc.data().date.content);
      console.log('--------------------------------');

      // address.push(doc.data().address.content); todo remove
      // receiptFields.push({ address: doc.data().address.content });

      // Update the Reactive receiptFields object

      receiptFields.merchantName = doc.data().merchantName.content;
      receiptFields.address = doc.data().address.content;
      receiptFields.category = doc.data().category.content;
      receiptFields.date = doc.data().date.content;
      receiptFields.subtotal = doc.data().subtotal.content;
      receiptFields.total = doc.data().total.content;
      receiptFields.totalTax = doc.data().totalTax.content;
    });
  } catch (err) {
    console.log(err, 'receipt fetch failed');
  }
}

//return/call getReceipt

// export const oneReceipt = getReceipt(receiptRef);
