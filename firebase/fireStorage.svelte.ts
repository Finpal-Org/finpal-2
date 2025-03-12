import { uploadBytesResumable, ref, getDownloadURL } from 'firebase/storage';
import { storage } from './firebaseConfig';

/**
 * Uploads a receipt image to Firebase Storage
 */

// Create the file metadata
const metadata = {
  contentType: 'image/jpeg'
};

// Upload file and metadata to the object 'images/{nahdi}.jpg'
// A Promise is like a container for a future value (in this case, the download URL)
//TODO: need to change File type?
export const uploadReceiptToStorage = (file: File): Promise<string> => {
  //param file is the receipt img
  return new Promise((resolve, reject) => {
    try {
      const fileName = `${Date.now()}_${file.name}`; //name img file

      const storageRef = ref(storage); //.parent?
      const receiptRef = ref(storage, 'receipts'); // imagesRef now points to 'receipts'

      const nahdiRef = ref(receiptRef, fileName);
      // const nahdiImagesRef = ref(storage, `receipts/${fileName}`);

      // for debugging
      const path = nahdiRef.fullPath;
      const name = nahdiRef.name;

      // Firebase's upload function (uploadBytesResumable) uses an event listener pattern with callbacks
      const uploadTask = uploadBytesResumable(nahdiRef, file, metadata);

      // Listen for state changes, errors, and completion of the upload. (debugging)
      uploadTask.on(
        'state_changed',
        (snapshot) => {
          // Get task progress, including the number of bytes uploaded and the total number of bytes to be uploaded
          const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          console.log(`upload is : ${progress}% Done`);
          switch (snapshot.state) {
            case 'paused':
              console.log('Upload is paused..');
              break;
            case 'running':
              console.log('Upload is running..');
              break;
          }
        },
        (error) => {
          switch (error.code) {
            // User doesn't have permission to access the object
            case 'storage/unauthorized':
              console.log('Unauthorized access to storage..');
              break;
            case 'storage/canceled':
              console.log('Cancelled..');
              break;
            case 'storage/unknown':
              console.log('Unknown..');
              break;
            //...
          }
        },
        async () => {
          // Upload completed successfully, now we can get the download URL
          try {
            const downloadUrl = await getDownloadURL(uploadTask.snapshot.ref);
            console.log(`File at ${downloadUrl}`);
            //- When upload succeeds, this sends the URL back to whoever called the function
            resolve(downloadUrl);
          } catch (e) {
            reject(e);
          }
        }
      );
    } catch (e) {
      console.log(`Failed General receipt upload${e}`);
      // promise failed;
      reject(e);
    }
  });
};

// const fileName=  `${Date.now()}_${file.name}` //dynamic img name
