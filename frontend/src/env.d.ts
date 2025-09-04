interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_WS_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
