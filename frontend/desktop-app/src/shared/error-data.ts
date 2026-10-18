// Копия ErrorData из frontend/src/shared/api/client.ts
export interface ErrorData {
  code: string;
  message: string;
  path: string;
  timestamp: string;
  traceId: string;
}
