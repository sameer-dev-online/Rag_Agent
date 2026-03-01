import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  APIResponse,
  APIError,
  ChatResponse,
  ConversationWithMessages,
  DocumentUploadResponse,
} from '@/types';
import { API_ENDPOINTS, DEFAULTS } from './constants';

/**
 * Centralized API client with typed methods
 */
class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor: Add API key
    this.client.interceptors.request.use(
      (config) => {
        const apiKey = process.env.NEXT_PUBLIC_API_KEY;
        if (apiKey) {
          config.headers['X-API-Key'] = apiKey;
        }
        return config;
      },
      (error) => {
        return Promise.reject(this.transformError(error));
      }
    );

    // Response interceptor: Transform errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        return Promise.reject(this.transformError(error));
      }
    );
  }

  /**
   * Transform axios error to APIError
   */
  private transformError(error: AxiosError): APIError {
    if (error.response) {
      // Server responded with error status
      const data = error.response.data as { message?: string; detail?: string; type?: string };
      return {
        message: data?.message || data?.detail || DEFAULTS.ERROR_MESSAGE,
        status: error.response.status,
        detail: data?.detail,
        type: data?.type,
      };
    } else if (error.request) {
      // Request made but no response
      return {
        message: DEFAULTS.NETWORK_ERROR,
        status: 0,
      };
    } else {
      // Error setting up request
      return {
        message: error.message || DEFAULTS.ERROR_MESSAGE,
        status: 0,
      };
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get<APIResponse<{ status: string }>>(
        API_ENDPOINTS.HEALTH
      );
      return response.data.success && response.data.data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Send a message and get response
   */
  async sendMessage(
    message: string,
    userId: string,
    conversationId?: string
  ): Promise<ChatResponse> {
    const response = await this.client.post<APIResponse<ChatResponse>>(API_ENDPOINTS.CHAT, {
      message,
      user_id: userId,
      conversation_id: conversationId || undefined,
    });

    return response.data.data;
  }

  /**
   * Get conversation with messages
   */
  async getConversation(conversationId: string, userId: string): Promise<ConversationWithMessages> {
    const response = await this.client.get<APIResponse<ConversationWithMessages>>(
      `${API_ENDPOINTS.CONVERSATIONS}/${conversationId}`,
      {
        params: { user_id: userId },
      }
    );

    return response.data.data;
  }

  /**
   * Upload a document
   */
  async uploadDocument(
    file: File,
    userId: string,
    title?: string,
    onProgress?: (progress: number) => void
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (title) {
      formData.append('title', title);
    }

    const response = await this.client.post<APIResponse<DocumentUploadResponse>>(
      API_ENDPOINTS.DOCUMENTS,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      }
    );

    return response.data.data;
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string, userId?: string): Promise<void> {
    await this.client.delete(`${API_ENDPOINTS.DOCUMENTS}/${documentId}`, {
      params: userId ? { user_id: userId } : {},
    });
  }
}

// Export singleton instance
export const apiClient = new APIClient();
