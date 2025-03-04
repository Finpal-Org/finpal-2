import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: 'AIzaSyAeSN-aBItuUN21fnbsklwdNrMCMNjWjJE',
  authDomain: 'finpal-5d6e8.firebaseapp.com',
  projectId: 'finpal-5d6e8',
  storageBucket: 'finpal-5d6e8.firebasestorage.app',
  messagingSenderId: '446406693977',
  appId: '1:446406693977:web:517d41f2c0e7a0cf880d48',
  measurementId: 'G-0N6KLHTSQZ',
};

// Initialize Firebase
const app = initializeApp(firebaseConfig); //configs
export const auth = getAuth(app); //auth
export const db = getFirestore(app);
