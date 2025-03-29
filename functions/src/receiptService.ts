// Import necessary Firebase modules
// import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase-admin/firestore';
// import { db } from '../../firebase/firebaseConfig';

// Safe type assertion for environment variables
const endpoint = process.env.VITE_AZURE_ENDPOINT || '';
const key = process.env.VITE_AZURE_KEY || '';
const analyzeUrl = `${endpoint}documentintelligence/documentModels/prebuilt-receipt:analyze?api-version=2024-11-30`;

// Initialize Firestore
const db = getFirestore();

// 1. Analyzes a receipt image using Azure Document Intelligence API
// 2. @param file The receipt file to analyze
// 3. @return Promise with the analysis result

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

    // Prepare the file data
    const fileData = await file.arrayBuffer();

    // Headers for the API request
    const headers = {
      'Ocp-Apim-Subscription-Key': key,
      'Content-Type': file.type
    };

    statusMessage = 'Analyzing receipt using Azure Document Intelligence...';
    console.log(statusMessage);

    // Step 1: Send the image to Azure for analysis
    const response = await fetch(analyzeUrl, {
      // give url + headers + method to azure
      method: 'POST',
      headers: headers,
      body: fileData
    });

    statusMessage = `Status code: ${response.status}`; // response success ?
    console.log(statusMessage);

    // Operation Accepted from azure...
    if (response.status === 202) {
      // Get the operation-location URL to check the operation status
      const operationLocation = response.headers.get('Operation-Location');
      statusMessage = `Operation started at: ${operationLocation}`;
      console.log(statusMessage);

      // get pollheaders from operation location...
      if (operationLocation) {
        const pollHeaders = {
          'Ocp-Apim-Subscription-Key': key
        };

        // Step 2: Poll until the analysis is complete
        statusMessage = 'Polling operation...';
        console.log(statusMessage);

        // Poll up to 10 times
        for (let i = 0; i < 10; i++) {
          // Wait 2 seconds between polls
          await new Promise((resolve) => setTimeout(resolve, 2000));

          // Check operation status
          const operationResponse = await fetch(operationLocation, {
            headers: pollHeaders // operation headers to identify our operation
          });

          statusMessage = `Poll status code: ${operationResponse.status}`;
          console.log(statusMessage);

          // when operation is done succesfully!
          if (operationResponse.status === 200) {
            // Parse the result
            const result = await operationResponse.json(); // get result from azure as json
            const status = result.status; // status for debugging
            statusMessage = `Operation status: ${status}`;
            console.log(statusMessage);

            if (status === 'succeeded') {
              statusMessage = 'Analysis succeeded!';
              console.log(statusMessage);
              const extracted = extractResults(result); // format the json result from azure

              // Save to Firestore
              if (Object.keys(extracted).length > 0 && !extracted.error) {
                await saveToFirestore(extracted);
                statusMessage = 'Results saved to Firestore!';
                console.log(statusMessage);
              }

              return extracted;
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
  } catch (error) {
    console.error('Error with Azure API call:', error);
    throw error;
  }
}

/**
 * Extracts relevant fields from the Azure Document Intelligence result
 * @param result The raw API result
 * @return Structured receipt data
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
      merchantName: 'MerchantName',
      address: 'MerchantAddress',
      phone: 'MerchantPhoneNumber',
      date: 'TransactionDate',
      time: 'TransactionTime',
      total: 'Total',
      subtotal: 'Subtotal',
      country: 'CountryRegion',
      taxDetails: 'TaxDetails',
      totalTax: 'TotalTax',
      tip: 'Tip',
      payment: 'PaymentType',
      currency: 'currencyCode',
      transactionId: 'TransactionId',
      items: 'Items',
      tags: 'Tags'
    };

    // Extract content & confidence fields from azure's fields
    for (const [ourField, azureField] of Object.entries(fieldMapping)) {
      if (azureField in fields) {
        // create our own fields in extracted, get their values from azures fields
        extracted[ourField] = {
          content: fields[azureField].content || '',
          confidence: fields[azureField].confidence || 0
        };
      }
    }

    // Handle receipt type / category
    if ('ReceiptType' in fields) {
      extracted.category = {
        content: fields.ReceiptType.valueString || 'Other', // valueString here is different for receipt type
        confidence: fields.ReceiptType.confidence || 0
      };
    }

    // Handle complex items data
    if ('Items' in fields) {
      const itemsField = fields.Items;
      const itemsArray = [];

      if ('valueArray' in itemsField) {
        for (const item of itemsField.valueArray || []) {
          const itemProperties: any = {};

          if ('valueObject' in item) {
            const valueObj = item.valueObject;

            if ('Description' in valueObj) {
              itemProperties.Description = {
                content: valueObj.Description.content || '',
                confidence: valueObj.Description.confidence || 0
              };
            }

            if ('Quantity' in valueObj) {
              itemProperties.Quantity = {
                content: valueObj.Quantity.content || '',
                confidence: valueObj.Quantity.confidence || 0
              };
            }

            if ('TotalPrice' in valueObj) {
              itemProperties.Amount = {
                content: valueObj.TotalPrice.content || '',
                confidence: valueObj.TotalPrice.confidence || 0,
                currency: valueObj.TotalPrice.valueCurrency?.currencyCode || 'SAR'
              };
            }
          }

          itemsArray.push(itemProperties);
        }
      }

      extracted.items = {
        content: itemsArray,
        confidence: itemsField.confidence || 0
      };
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

  return extracted;
}

/**
 * Saves receipt data to Firestore
 * @param data The extracted receipt data
 * @return Promise that resolves when data is saved
 */
export async function saveToFirestore(data: any): Promise<void> {
  try {
    const docRef = await db.collection('receipts').add(data); // add receipt in a new doc inside receipt collection
    console.log('Receipt saved to Firestore with ID:', docRef.id);
  } catch (error) {
    console.error('Error saving to Firestore:', error);
    throw error;
  }
}
