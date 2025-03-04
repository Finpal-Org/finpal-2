import {
  collection,
  getDoc,
  getDocs,
  documentId,
  DocumentReference,
} from 'firebase/firestore';
import { db } from './firebaseConfig';

const receiptCollection = collection(db, 'receipts');

export let receiptFields = {
  merchantName: 'test-merchant',
  address: 'test-address',
  category: 'test-category',
  date: 'test-date',
  subtotal: 'test-subtotal',
  total: 'test-total',
  totalTax: 'test-totalTax',
};

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

      // fill the object while looping
      receiptFields = {
        merchantName: doc.data().merchantName.content,
        address: doc.data().address.content,
        category: doc.data().category.content,
        date: doc.data().date.content,
        subtotal: doc.data().subtotal.content,
        total: doc.data().total.content,
        totalTax: doc.data().totalTax.content,
      };
      // console.log("Exists: ", doc.exists());
    });
  } catch (err) {
    console.log(err, 'receipt fetch failed');
  }
}

//return/call getReceipt

// export const oneReceipt = getReceipt(receiptRef);
