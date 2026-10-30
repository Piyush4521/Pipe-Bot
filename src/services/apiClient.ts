/**
 * PipeBot API Client Foundation
 * Configured for future integration with Python FastAPI backend (Stage 5).
 */

export interface ApiClientConfig {
  baseUrl: string;
  timeoutMs: number;
}

export const DEFAULT_API_CONFIG: ApiClientConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  timeoutMs: 10000,
};

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public responseBody?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Low-level fetch wrapper with error handling and JSON decoding.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  config: ApiClientConfig = DEFAULT_API_CONFIG
): Promise<T> {
  const url = `${config.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new ApiError(
      `API request failed with status ${response.status}: ${response.statusText}`,
      response.status,
      errorBody
    );
  }

  return response.json() as Promise<T>;
}

