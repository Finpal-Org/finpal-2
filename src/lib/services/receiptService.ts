// Import necessary Firebase modules
// import { initializeApp } from 'firebase/app';
import { collection, addDoc } from 'firebase/firestore';
import { db } from '../../../firebase/firebaseConfig';
import { standardizeCategory } from '../utils/categoryMapping';
import { uploadReceiptToStorage } from '../../../firebase/fireStorage.svelte';

// Safe type assertion for environment variables

// Azure Doc Ai Information, vite fetches .env values from our root
const endpoint = import.meta.env.VITE_AZURE_ENDPOINT;
const key = import.meta.env.VITE_AZURE_KEY;
const analyzeUrl = `${endpoint}documentintelligence/documentModels/prebuilt-receipt:analyze?api-version=2024-11-30`;

// Default fallback image URL
const DEFAULT_IMAGE_URL = '/src/assets/contoso-receipt.png';

/**
 * Analyzes a receipt image using Azure Document Intelligence API
 * @param file The receipt file to analyze
 * @returns Promise with the analysis result
 */
export async function analyzeReceipt(file: File): Promise<any> {
  let statusMessage = 'Preparing to analyze receipt...';
  console.log(statusMessage);

  try {
    // Check file size (must be less than 4MB)
    const fileSizeMB = file.size / (1024 * 1024);
    statusMessage = `File size: ${fileSizeMB.toFixed(2)} MB`;
    console.log(statusMessage);

    if (fileSizeMB > 4) {
      throw new Error('File size exceeds 4MB limit');
    }

    statusMessage = 'Processing receipt...';
    console.log(statusMessage);

    // Run Azure analysis and Firebase upload in parallel
    try {
      const [extracted, imageUrl] = await Promise.all([
        analyzeReceiptWithAzure(file), // Azure analysis
        uploadReceiptToStorage(file).catch((error) => {
          console.error('Image upload failed, using default image:', error);
          return DEFAULT_IMAGE_URL; // Use default image if upload fails
        })
      ]);

      // If we have valid extraction results, save to Firestore with image URL
      if (Object.keys(extracted).length > 0 && !extracted.error) {
        // Add image URL to the extracted data
        extracted.imageUrl = imageUrl;

        // Save to Firestore
        await saveToFirestoreDirectly(extracted);
        statusMessage = 'Results saved to Firestore!';
        console.log(statusMessage);
      }

      return extracted;
    } catch (error) {
      // If Azure analysis fails, we won't try to save anything
      console.error('Analysis failed:', error);
      throw error;
    }
  } catch (error) {
    console.error('Error processing receipt:', error);
    throw error;
  }
}

/**
 * Handles only the Azure Document Intelligence analysis part
 * @param file The receipt file to analyze
 * @returns Promise with the extracted data
 */
async function analyzeReceiptWithAzure(file: File): Promise<any> {
  // Prepare the file data
  const fileData = await file.arrayBuffer();

  // Headers for the API request
  const headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Content-Type': file.type
  };

  console.log('Analyzing receipt using Azure Document Intelligence...');

  // Step 1: Send the image to Azure for analysis
  const response = await fetch(analyzeUrl, {
    //give url + headers + method to azure
    method: 'POST',
    headers: headers,
    body: fileData
  });

  console.log(`Status code: ${response.status}`);

  // Operation Accepted from azure...
  if (response.status === 202) {
    // Get the operation-location URL to check the operation status
    const operationLocation = response.headers.get('Operation-Location');
    console.log(`Operation started at: ${operationLocation}`);

    // get pollheaders from operation location...
    if (operationLocation) {
      const pollHeaders = {
        'Ocp-Apim-Subscription-Key': key
      };

      // Step 2: Poll until the analysis is complete
      // console.log('Polling operation...');

      // Poll up to 10 times
      for (let i = 0; i < 10; i++) {
        // Wait 2 seconds between polls
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Check operation status
        const operationResponse = await fetch(operationLocation, {
          headers: pollHeaders //operation headers to identify our operation
        });

        console.log(`Poll status code: ${operationResponse.status}`);

        // when operation is done succesfully!
        if (operationResponse.status === 200) {
          // Parse the result
          const result = await operationResponse.json(); // get result from azure as json
          const status = result.status; //status for debugging
          console.log(`Operation status: ${status}`);

          if (status === 'succeeded') {
            console.log('Analysis succeeded!');
            return extractResults(result); // format the json result from azure
          } else if (status === 'failed') {
            throw new Error(`Analysis failed: ${JSON.stringify(result.errors)}`);
          }
        } else {
          throw new Error(`Error response: ${await operationResponse.text()}`);
        }
      }
      throw new Error('Maximum polling attempts reached without success');
    }
  } else {
    throw new Error(`Error response: ${await response.text()}`);
  }
}

/**
 * Extracts relevant fields from the Azure Document Intelligence result
 * @param result The raw API result
 * @returns Structured receipt data
 */
export function extractResults(result: any) {
  const extracted: any = {};

  console.log('\nAPI RESPONSE STRUCTURE:');

  // Debug information
  if ('analyzeResult' in result) {
    const analyzeResult = result.analyzeResult || {};

    if ('documents' in analyzeResult) {
      const documents = analyzeResult.documents || [];
      if (documents.length) {
        // debug: check fields avaiable in receipt doc
        console.log('Document fields available:', Object.keys(documents[0].fields || {}));
      }
    }
  }

  try {
    // Navigate to document fields
    const documents = result.analyzeResult?.documents || [];
    if (!documents.length) {
      return { error: 'No documents found in Azure result' };
    }

    // First document (the Result)
    const document = documents[0];
    const fields = document.fields || {};

    // Field mapping (our field names to Azure's field names)
    const fieldMapping: Record<string, string> = {
      date: 'TransactionDate',
      time: 'TransactionTime',
      total: 'Total',
      subtotal: 'Subtotal',
      countryRegion: 'CountryRegion',
      taxDetails: 'TaxDetails',
      tax: 'TotalTax',
      tip: 'Tip',
      currency: 'currencyCode',
      invoice_number: 'TransactionId'
    };

    // Create vendor object
    extracted.vendor = {
      name: fields.MerchantName?.content || '',
      address: fields.MerchantAddress?.content || '',
      phone: fields.MerchantPhoneNumber?.content || ''
    };

    // Extract content for regular fields
    for (const [ourField, azureField] of Object.entries(fieldMapping)) {
      if (azureField in fields) {
        extracted[ourField] = fields[azureField].content || '';
      }
    }

    // Handle receipt type / category
    if ('ReceiptType' in fields) {
      // Get raw category and standardize it
      const rawCategory = fields.ReceiptType.valueString || 'Other';
      extracted.category = standardizeCategory(rawCategory);
    }

    // Generate a unique receipt_id
    extracted.receipt_id = crypto.randomUUID();

    // Special handling for TaxDetails to extract rate, description, and netAmount
    if ('TaxDetails' in fields) {
      const taxDetailsField = fields.TaxDetails;
      const taxDetailsArray = [];

      if ('valueArray' in taxDetailsField && Array.isArray(taxDetailsField.valueArray)) {
        for (const taxDetail of taxDetailsField.valueArray || []) {
          const taxDetailProps: any = {};

          if ('valueObject' in taxDetail) {
            const valueObj = taxDetail.valueObject;

            if ('Rate' in valueObj) {
              taxDetailProps.rate = valueObj.Rate.content || '';
            }

            if ('Description' in valueObj) {
              taxDetailProps.description = valueObj.Description.content || '';
            }

            if ('NetAmount' in valueObj) {
              taxDetailProps.netAmount = valueObj.NetAmount.content || '';
            }
          }

          taxDetailsArray.push(taxDetailProps);
        }
      }

      if (taxDetailsArray.length > 0) {
        extracted.taxDetailsArray = taxDetailsArray;
        // todo remove debug
        console.log('Tax Details Array extracted:', taxDetailsArray);
      }
    }

    // Special handling for Payments array
    if ('Payments' in fields) {
      const paymentsField = fields.Payments;

      // Initialize payment object
      extracted.payment = {
        display_name: '',
        type: ''
      };

      // Handle the array structure from the API
      if (
        'valueArray' in paymentsField &&
        Array.isArray(paymentsField.valueArray) &&
        paymentsField.valueArray.length > 0
      ) {
        // Get first payment method
        const payment = paymentsField.valueArray[0];

        if ('valueObject' in payment) {
          const valueObj = payment.valueObject;

          if ('Method' in valueObj) {
            const method = valueObj.Method.content || valueObj.Method.valueString || '';
            extracted.payment.display_name = method;
            extracted.payment.type = method.toLowerCase();
          }
        }
      } else if ('content' in paymentsField) {
        // Alternative format where just content is available
        const method = paymentsField.content || '';
        extracted.payment.display_name = method;
        extracted.payment.type = method.toLowerCase();
      }
    }

    // Handle complex items data
    if ('Items' in fields) {
      const itemsField = fields.Items;
      extracted.line_items = [];

      if ('valueArray' in itemsField) {
        for (let i = 0; i < (itemsField.valueArray || []).length; i++) {
          const item = itemsField.valueArray[i];
          const lineItem = {
            id: i + 1,
            description: '',
            quantity: 1,
            total: 0
          };

          if ('valueObject' in item) {
            const valueObj = item.valueObject;
            if ('Description' in valueObj) {
              lineItem.description = valueObj.Description.content || '';
            }
            if ('Quantity' in valueObj) {
              lineItem.quantity = valueObj.Quantity.content || 1;
            }
            if ('TotalPrice' in valueObj) {
              lineItem.total = valueObj.TotalPrice.content || 0;
            }
          }

          extracted.line_items.push(lineItem);
        }
      }
    }

    // Handle tags, todo do we need?
    if ('Tags' in result.analyzeResult) {
      extracted.tags = result.analyzeResult.Tags || {};
    }

    // Handle document type / category ,TODO: what needs to be done?
    // const docType = document.docType || '';
    // extracted.category = {
    //   content: docType,
    //   confidence: document.confidence || 0,
    // };

    // Add creation timestamp
    extracted.createdTime = new Date();
  } catch (error) {
    return {
      error: `Extracting fields error: ${error instanceof Error ? error.message : String(error)}`
    };
  }
  console.log('The Flat Extracted Object ', extracted);

  return extracted;
}

// Saves receipt data directly to Firestore without additional processing
async function saveToFirestoreDirectly(data: any): Promise<string> {
  try {
    const docRef = await addDoc(collection(db, 'receipts'), data);
    // console.log('Receipt saved to Firestore with ID:', docRef.id);
    return docRef.id;
  } catch (error) {
    console.error('Error saving to Firestore:', error);
    throw error;
  }
}

// The original saveToFirestore function is kept for backward compatibility
export async function saveToFirestore(data: any, imageFile?: File): Promise<string> {
  try {
    // If we have an image file, upload it to Firebase Storage first
    if (imageFile) {
      try {
        const imageUrl = await uploadReceiptToStorage(imageFile);
        data.imageUrl = imageUrl; // Add the image URL to the receipt data
      } catch (error) {
        console.error('Image upload failed, using default image:', error);
        data.imageUrl = DEFAULT_IMAGE_URL; // Use default image if upload fails
      }
    }

    return saveToFirestoreDirectly(data);
  } catch (error) {
    console.error('Error saving to Firestore:', error);
    throw error;
  }
}
