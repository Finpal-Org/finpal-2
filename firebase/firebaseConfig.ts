import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  // todo maybe hide them later
  apiKey: 'AIzaSyDomDNnxl85tSagZ-1eGmFcy40R4PvBJPI',
  authDomain: 'finpal-4c883.firebaseapp.com',
  projectId: 'finpal-4c883',
  storageBucket: 'finpal-4c883.firebasestorage.app',
  messagingSenderId: '332682233191',
  appId: '1:332682233191:web:fa19475e3265c005261bc2',
  measurementId: 'G-M21S6JPSN3'
};

// Initialize Firebase
const app = initializeApp(firebaseConfig); //configs
export const auth = getAuth(app); //auth ref
export const db = getFirestore(app); //db ref
export const storage = getStorage(app); // storage ref
