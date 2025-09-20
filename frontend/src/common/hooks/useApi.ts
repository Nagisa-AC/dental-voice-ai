/**
 * Custom Hook for API Calls
 * 
 * Provides a standardized way to make API calls with loading states,
 * error handling, and response caching.
 */

import { useState, useEffect, useCallback } from 'react';
import axios, { AxiosResponse, AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  immediate?: boolean;
  cache?: boolean;
  cacheKey?: string;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: unknown[]) => Promise<T | null>;
  reset: () => void;
}

// Simple in-memory cache
const cache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useApi<T = unknown>(
  apiCall: (...args: unknown[]) => Promise<AxiosResponse<T>>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const { immediate = false, cache: useCache = false, cacheKey } = options;
  
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (...args: unknown[]): Promise<T | null> => {
    const key = cacheKey || JSON.stringify(args);
    
    // Check cache first
    if (useCache && cacheKey) {
      const cached = cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setState(prev => ({ ...prev, data: cached.data, loading: false, error: null }));
        return cached.data;
      }
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiCall(...args);
      const data = response.data;
      
      // Cache the result
      if (useCache && cacheKey) {
        cache.set(cacheKey, { data, timestamp: Date.now() });
      }
      
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const axiosError = error as AxiosError;
      const errorMessage = (axiosError.response?.data as { message?: string })?.message || axiosError.message || 'An error occurred';
      
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return null;
    }
  }, [apiCall, useCache, cacheKey]);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hook for GET requests
export function useGet<T = unknown>(
  url: string,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const apiCall = useCallback(() => axios.get<T>(url), [url]);
  return useApi(apiCall, options);
}

// Hook for POST requests
export function usePost<T = unknown, D = unknown>(
  url: string,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const apiCall = useCallback((data: D) => axios.post<T>(url, data), [url]);
  return useApi(apiCall, options);
}

// Hook for PUT requests
export function usePut<T = unknown, D = unknown>(
  url: string,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const apiCall = useCallback((data: D) => axios.put<T>(url, data), [url]);
  return useApi(apiCall, options);
}

// Hook for DELETE requests
export function useDelete<T = unknown>(
  url: string,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const apiCall = useCallback(() => axios.delete<T>(url), [url]);
  return useApi(apiCall, options);
}
