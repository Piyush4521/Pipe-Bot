/**
 * Standardized API Error Handling
 */

export class ApiError extends Error {
  public readonly statusCode?: number;
  public readonly endpoint?: string;
  public readonly responseBody?: unknown;
  public readonly isNetworkError: boolean;
  public readonly isTimeout: boolean;

  constructor(params: {
    message: string;
    statusCode?: number;
    endpoint?: string;
    responseBody?: unknown;
    isNetworkError?: boolean;
    isTimeout?: boolean;
  }) {
    super(params.message);
    this.name = 'ApiError';
    this.statusCode = params.statusCode;
    this.endpoint = params.endpoint;
    this.responseBody = params.responseBody;
    this.isNetworkError = params.isNetworkError ?? false;
    this.isTimeout = params.isTimeout ?? false;
  }
}

export function createNetworkError(endpoint: string, originalError?: unknown): ApiError {
  return new ApiError({
    message: `Network failure: Unable to reach endpoint at ${endpoint}. Ensure local backend server is running.`,
    endpoint,
    isNetworkError: true,
    responseBody: originalError,
  });
}

export function createTimeoutError(endpoint: string, timeoutMs: number): ApiError {
  return new ApiError({
    message: `Request timeout: Endpoint ${endpoint} did not respond within ${timeoutMs}ms.`,
    endpoint,
    isTimeout: true,
  });
}

