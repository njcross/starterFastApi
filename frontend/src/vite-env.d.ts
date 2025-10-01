/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ORIGIN: string
  // add more VITE_ vars here as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
