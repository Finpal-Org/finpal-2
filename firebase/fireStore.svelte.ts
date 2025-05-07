import {
  collection,
  getDocs,
  orderBy,
  query,
  addDoc,
  serverTimestamp,
  where,
  doc,
  updateDoc,
  deleteDoc,
  setDoc
} from 'firebase/firestore';
import { db } from './firebaseConfig';
import type { ReceiptData } from '../src/types';
import { getCurrentUser } from './fireAuth';
import { generateUniqueId } from '../src/lib/utils/idGenerator';
// import type ReceiptField from '../src/lib/Receipt.svelte';

export let receipts: ReceiptData[] = $state([]); // init reactive receipts as empty array

const receiptCollection = collection(db, 'receipts'); //receipt collection ref

export async function getReceipts() {
  //fetch receipts from firestore
  try {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      console.log('No user logged in, cannot fetch receipts');
      receipts.length = 0;
      return;
    }

    // Get only receipts for the current user
    const userReceiptsQuery = query(receiptCollection, where('user_id', '==', currentUser.uid));

    const userReceiptDocs = await getDocs(userReceiptsQuery);

    // Clear current receipts
    receipts.length = 0;

    // Process user's receipts
    const processedReceipts: ReceiptData[] = [];

    userReceiptDocs.docs.forEach((doc) => {
      // Extract all the data first
      const rawData = doc.data();

      interface item {
        Description?: string;
        Amount?: string;
        Currency?: string;
        Quantity?: string;
        description?: string;
        amount?: string;
        currency?: string;
        quantity?: string;
        warranty?: {
          hasWarranty: boolean;
          periodMonths: number;
          expiryDate?: string;
        };
      }

      // item empty by default
      let itemsProperties = [];

      // if there are items
      if (rawData && (rawData.items || rawData.line_items)) {
        const itemsSource = rawData.line_items || rawData.items;
        //if there are items nested
        if (itemsSource && itemsSource.content) {
          itemsProperties = itemsSource.content.map((item: item) => ({
            description: item.description || item.Description || '',
            amount: item.amount || item.Amount || '',
            currency: item.currency || item.Currency || 'SAR',
            quantity: item.quantity || item.Quantity || '',
            warranty: item.warranty || undefined
          }));
          // else items flat
        } else {
          itemsProperties = itemsSource.map((item: item) => ({
            description: item.description || item.Description || '',
            amount: item.amount || item.Amount || '',
            currency: item.currency || item.Currency || 'SAR',
            quantity: item.quantity || item.Quantity || '',
            warranty: item.warranty || undefined
          }));
        }
      }

      // Build object from safe variables
      const safeReceipt = {
        // Use receipt_id as the main identifier
        receipt_id: rawData.receipt_id,
        receipt_image: rawData.receipt_image || rawData.imageUrl || '',
        category: rawData.category || 'Other',
        date: rawData.date || 'Unknown',
        invoice_number: rawData.invoice_number || rawData.transactionId || '',
        is_duplicate: rawData.is_duplicate || false,
        note: rawData.note || '',

        // Money fields
        subtotal: rawData.subtotal || '0',
        tax: rawData.tax || rawData.totalTax || '0',
        total: rawData.total || '0',
        tip: rawData.tip || '0',
        currency: rawData.currency || 'SAR',

        // Vendor information
        vendor: {
          name: rawData.vendor?.name || rawData.merchantName || 'Unknown',
          address: rawData.vendor?.address || rawData.address || 'Unknown',
          phone: rawData.vendor?.phone || rawData.phone || 'Unknown',
          logo: rawData.vendor?.logo || ''
        },

        // Line items
        line_items: itemsProperties || [],

        // Payment information
        payment: rawData.payment || { type: 'Unknown' },

        // Other fields
        createdTime: rawData.createdTime
          ? typeof rawData.createdTime.toDate === 'function'
            ? rawData.createdTime.toDate()
            : new Date(rawData.createdTime)
          : null, // Use null for receipts without createdTime
        imageUrl: rawData.imageUrl || rawData.receipt_image || '',
        user_id: rawData.user_id || ''
      };

      processedReceipts.push(safeReceipt);
    });

    // Sort by createdTime (newest first), receipts without createdTime at the end
    processedReceipts.sort((a, b) => {
      // If both have createdTime, compare normally
      if (a.createdTime && b.createdTime) {
        const dateA = a.createdTime instanceof Date ? a.createdTime : new Date(a.createdTime);
        const dateB = b.createdTime instanceof Date ? b.createdTime : new Date(b.createdTime);
        return dateB.getTime() - dateA.getTime(); // newest first
      }
      // If a has no createdTime, put it at the end
      if (!a.createdTime && b.createdTime) return 1;
      // If b has no createdTime, put it at the end
      if (a.createdTime && !b.createdTime) return -1;
      // If neither has createdTime, keep original order
      return 0;
    });

    // Add all processed receipts to the state array
    receipts.push(...processedReceipts);

    console.log(`Loaded ${receipts.length} receipts from Firestore`);
  } catch (err) {
    console.log(err, 'receipt fetch failed');
  }
}

// Function to add a new receipt with image URL
export async function addReceiptWithImage(receiptData: ReceiptData, imageUrl: string) {
  try {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      throw new Error('No user logged in. Cannot save receipt.');
    }

    // Generate a unique receipt_id if not provided
    const receipt_id = receiptData.receipt_id || generateUniqueId();

    // Add imageUrl, receipt_id, and user_id to the receipt data
    const receiptWithImage = {
      ...receiptData,
      receipt_id,
      imageUrl,
      user_id: currentUser.uid,
      createdTime: serverTimestamp()
    };

    // Use doc() and setDoc() to create a document with a specific ID
    const docRef = doc(db, 'receipts', receipt_id);
    await setDoc(docRef, receiptWithImage);

    console.log('Receipt added with ID: ', receipt_id);

    // Refresh receipts list
    await getReceipts();

    return receipt_id;
  } catch (error) {
    console.error('Error adding receipt: ', error);
    throw error;
  }
}

// Function to update an existing receipt
export async function updateReceipt(receiptId: string, receiptData: ReceiptData): Promise<void> {
  try {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      throw new Error('No user logged in. Cannot update receipt.');
    }

    // Ensure the receipt data has the correct receipt_id
    const dataToUpdate = {
      ...receiptData,
      receipt_id: receiptId, // Make sure receipt_id matches document ID
      user_id: currentUser.uid
    };

    // Get reference to the receipt document
    const receiptRef = doc(db, 'receipts', receiptId);

    // Use setDoc with merge option to update the document
    // This ensures all fields are properly updated and preserves fields not in dataToUpdate
    await setDoc(receiptRef, dataToUpdate, { merge: true });

    // Refresh receipts list
    await getReceipts();

    console.log('Receipt updated with ID: ', receiptId);
  } catch (error) {
    console.error('Error updating receipt: ', error);
    throw error;
  }
}

// Function to delete a receipt
export async function deleteReceipt(receiptId: string): Promise<void> {
  try {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      throw new Error('No user logged in. Cannot delete receipt.');
    }

    // Get reference to the receipt document
    // We use the receiptId as the document ID
    const receiptRef = doc(db, 'receipts', receiptId);

    // Delete the document
    await deleteDoc(receiptRef);

    // Refresh receipts list
    await getReceipts();

    console.log('Receipt deleted with ID: ', receiptId);
  } catch (error) {
    console.error('Error deleting receipt: ', error);
    throw error;
  }
}

//return/call getReceipt

// export const oneReceipt = getReceipt(receiptRef);
