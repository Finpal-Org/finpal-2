import { onObjectFinalized } from 'firebase-functions/v2/storage';
import * as admin from 'firebase-admin';
import path from 'path';
import * as fs from 'fs-extra';
import * as mime from 'mime-types';
import { analyzeReceipt } from './receiptService';

// INIT ADMIN
admin.initializeApp();

// This function runs automatically when files are uploaded to Firebase Storage
export const processUploadReceipt = onObjectFinalized(async (event) => {
  //Validtion: check if its inside receipts folder
  if (!event.data.name || !event.data.name.startsWith('receipts/')) {
    console.log('Not in Receipt folder...');
    return null;
  }

  try {
    console.log('proccessing receipt...', event.data.name);
    //1. get file information
    const filePath = event.data.name; // file path
    const fileName = path.basename(filePath);
    const tempFilePath = `/tmp/${fileName}`; // tempFilePath is just a temporary place where your function downloads the file

    // 2. Download the receipt file from Storage to function's temporary storage
    const bucket = admin.storage().bucket(event.data.bucket);
    await bucket.file(filePath).download({ destination: tempFilePath }); //take OG file path, download it inside temp path
    console.log('File downloaded temporarly in: ', tempFilePath);

    //2.1 Create a File-like object that Azure can work with
    const fileBuffer = await fs.readFile(tempFilePath);
    const fileSize = (await fs.stat(tempFilePath)).size;
    const fileType = mime.lookup(tempFilePath) || 'application/octet-stream';

    // mock a File type for typescript
    const mockFile = {
      name: fileName,
      size: fileSize,
      type: fileType,
      arrayBuffer: async () => fileBuffer
      // Add any other File properties your code uses
    };

    console.log(`Created File-like object: ${fileName}, ${fileSize} bytes, ${fileType}`);

    //4. process the file
    const result = await analyzeReceipt(mockFile); //TODO: currently forcing a file mock as arg

    console.log('Receipt analysis complete!', result);

    //5. Clean the temp downloaded file
    await fs.unlink(tempFilePath);
    console.log('Temporary file cleaned.. > End of receipt analysis...');

    return result;
  } catch (e) {
    console.log('Receipt analysis failed..', e);
    return null;
  }
});
