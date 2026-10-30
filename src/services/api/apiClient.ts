import { APP_CONFIG } from '@/constants/config';
import { ApiError, createNetworkError, createTimeoutError } from './apiErrors';

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
  timeoutMs?: number;
}

/**
 * Standardized Fetch Client for Python FastAPI Backend
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    body,
    params,
    timeoutMs = APP_CONFIG.apiTimeoutMs,
    headers: customHeaders,
    ...fetchOptions
  } = options;

  // Construct URL with query parameters
  let url = `${APP_CONFIG.apiBaseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined) {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  // Set standard headers
  const headers = new Headers(customHeaders);
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Setup abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorBody: unknown;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = await response.text();
      }

      throw new ApiError({
        message: `API request to ${endpoint} failed with HTTP ${response.status}`,
        statusCode: response.status,
        endpoint,
        responseBody: errorBody,
      });
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    clearTimeout(timeoutId);

    if (err instanceof ApiError) {
      throw err;
    }

    if (err instanceof DOMException && err.name === 'AbortError') {
      throw createTimeoutError(endpoint, timeoutMs);
    }

    throw createNetworkError(endpoint, err);
  }
}

