/// <reference types="svelte" />
/// <reference types="vite/client" />

// JUST TYPESCRIPT TYPES FOR ENV
interface ImportMetaEnv {
  readonly VITE_FIREBASE_API_KEY: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN: string;
  readonly VITE_FIREBASE_PROJECT_ID: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  readonly VITE_FIREBASE_APP_ID: string;
  readonly VITE_AZURE_ENDPOINT: string;
  readonly VITE_AZURE_KEY: string;
  readonly VITE_DEEPSEEK_API_KEY: string;
  readonly VITE_DEEPSEEK_SERVER_URL: string;
}

interface ImportMeta {
  // HERE WE JUST USE env Type
  readonly env: ImportMetaEnv;
}
