import { auth } from './firebaseConfig';
import {
  GoogleAuthProvider,
  signInWithPopup,
  onAuthStateChanged as firebaseOnAuthStateChanged,
  createUserWithEmailAndPassword as firebaseCreateUser,
  signInWithEmailAndPassword as firebaseSignIn,
  signOut as firebaseSignOut,
  updateProfile
} from 'firebase/auth';
import type { User, UserCredential } from 'firebase/auth';
import { collection, doc, getDoc, setDoc, serverTimestamp } from 'firebase/firestore';
import { db } from './firebaseConfig';
import type { UserProfile } from '../src/types';

//user details
const emailInput: HTMLInputElement = document.getElementById('email') as HTMLInputElement; //todo ts why string isnt viable?
const passwordInput: HTMLInputElement = document.getElementById('password') as HTMLInputElement;

//Auth Buttons
const signUpButton = document.getElementById('signUpButton');
const signInButton = document.getElementById('signInButton');

const signUpWithGoogle = document.getElementById('signUpWithGoogle');

const signOutButton = document.getElementById('signOutButton');

//Providers
const googleProvider = new GoogleAuthProvider();

const emailDisplayName: string = '';
// Helper function to show error messages

// Authentication service functions

/**
 * - Create a user profile in Firestore
 *  1 userId User ID from Firebase Auth
 *  2 email User email
 *  3 displayName Optional display name
 *  4 Return Promise that resolves when the profile is created
 */
export async function createUserProfile(
  userId: string,
  email: string,
  displayName?: string
): Promise<void> {
  try {
    const userRef = doc(db, 'users', userId);

    // Check if the user profile already exists
    const userDoc = await getDoc(userRef);

    if (userDoc.exists()) {
      console.log('User Account already exists');
      return;
    }

    // Create a new user profile
    const userProfile: UserProfile = {
      user_id: userId,
      email: email,
      full_name: displayName || email.split('@')[0],
      creation_date: new Date(),
      did_complete_onboarding: false,
      did_visit_chatbot_screen: false
    };

    await setDoc(userRef, {
      ...userProfile,
      creation_date: serverTimestamp() // Use server timestamp for consistent timing
    });

    console.log('User profile created successfully');
  } catch (error) {
    console.error('Error creating user profile:', error);
    throw error;
  }
}

/**
 * Create a new user with email and password
 * @param email User email
 * @param password User password
 * @param displayName Optional display name
 * @returns Promise resolving to user credentials
 */
export async function createUser(
  email: string,
  password: string,
  displayName?: string
): Promise<UserCredential> {
  try {
    // Create the user
    const userCredential = await firebaseCreateUser(auth, email, password);

    // Set display name if provided or use email username
    if (auth.currentUser) {
      await updateProfile(auth.currentUser, {
        displayName: displayName || email.split('@')[0]
      });

      // Create user profile in Firestore
      await createUserProfile(auth.currentUser.uid, email, displayName || email.split('@')[0]);
    }

    return userCredential;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
}

/**
 * Sign in with Google popup
 * @returns Promise resolving to user credentials
 */
export async function signInWithGoogle(): Promise<UserCredential> {
  try {
    const googleProvider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, googleProvider);

    // Create user profile if it doesn't exist
    if (userCredential.user) {
      await createUserProfile(
        userCredential.user.uid,
        userCredential.user.email || '',
        userCredential.user.displayName || undefined
      );
    }

    return userCredential;
  } catch (error) {
    console.error('Error signing in with Google:', error);
    throw error;
  }
}

/**
 * Sign in with email and password
 * @param email User email
 * @param password User password
 * @returns Promise resolving to user credentials
 */
export async function signInWithEmail(email: string, password: string): Promise<UserCredential> {
  try {
    return await firebaseSignIn(auth, email, password);
  } catch (error) {
    console.error('Error signing in with email:', error);
    throw error;
  }
}

/**
 * Sign out the current user
 * @returns Promise that resolves when sign out is complete
 */
export async function signOut(): Promise<void> {
  try {
    return await firebaseSignOut(auth);
  } catch (error) {
    console.error('Error signing out:', error);
    throw error;
  }
}

/**
 * Get the current authenticated user
 * @returns The current user or null if not authenticated
 */
export function getCurrentUser(): User | null {
  return auth.currentUser;
}

/**
 * Set up an auth state change listener
 * @param callback Function to call when auth state changes
 * @returns Unsubscribe function
 */
export function onAuthStateChanged(callback: (user: User | null) => void): () => void {
  return firebaseOnAuthStateChanged(auth, callback);
}

/**
 * Update the current user's profile
 * @param displayName New display name
 * @returns Promise that resolves when update is complete
 */
export async function updateUserProfile(displayName: string): Promise<void> {
  if (!auth.currentUser) {
    throw new Error('No user is currently signed in');
  }

  try {
    return await updateProfile(auth.currentUser, { displayName });
  } catch (error) {
    console.error('Error updating profile:', error);
    throw error;
  }
}

// Provide access to auth for advanced usage if needed
export { auth };

//on SignUp With Google Click
if (signUpWithGoogle) {
  signUpWithGoogle.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      await signInWithGoogle();
      console.log('signed in with Google!');
      //redirect to home page
      window.location.href = '/index.html';
    } catch (err) {
      console.log('Error signing in with Google', err);
    }
  });
}
// on SignUp with email And password click
if (signUpButton) {
  signUpButton.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      if (emailInput && passwordInput) {
        const email = (emailInput as HTMLInputElement).value;
        const password = (passwordInput as HTMLInputElement).value;

        await createUser(email, password);

        console.log('signed Up with email and password Success');
        //redirect to home page todo
        window.location.href = '/index.html';
      }
    } catch (err) {
      console.log('Error signing Up with email and password', err);
    }
  });
}
if (signInButton) {
  //will not be clicked unless valid
  signInButton.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      if (emailInput && passwordInput) {
        const email = (emailInput as HTMLInputElement).value;
        const password = (passwordInput as HTMLInputElement).value;

        await signInWithEmail(email, password);

        console.log('signed in with email and password Success');
        //redirect to home page todo
        window.location.href = '/index.html';
      }
    } catch (err) {
      console.log('Error signing in with email and password', err);
    }
  });
}

//on SignOut Click
if (signOutButton) {
  //oneventlisten "click"
  signOutButton.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      await signOut();

      window.location.href = '/index.html';

      console.log('Sign out success!');
    } catch (err) {
      console.log('Error signing out', err);
    }
  });
}

//fetch user info
onAuthStateChanged((user) => {
  //fire auth user name
  const displayName: string = user?.displayName || emailDisplayName.split('@')[0] || 'Guest'; //get all chars untill @ sign

  //username element in html
  const userNameElement = document.getElementById('userName');

  if (userNameElement) {
    //inside sidebar
    console.log('displayed name is ', displayName);
    return (userNameElement.innerText = `Welcome, ${displayName}`);
  }
});
