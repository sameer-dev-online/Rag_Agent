/**
 * Generic API response wrapper from FastAPI backend
 */
export interface APIResponse<T> {
  success: boolean;
  message: string;
  status: number;
  data: T;
}

/**
 * Error structure for API failures
 */
export interface APIError {
  message: string;
  status: number;
  detail?: string;
  type?: string;
}
