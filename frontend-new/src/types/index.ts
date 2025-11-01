// Simple types for the application
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  error?: boolean;
}

export interface PDFDocument {
  uuid: string;
  name: string;
  displayName: string;
  uploadedAt: Date;
  hash?: string;  // File content hash for chat history identification
}

export interface ChatResponse {
  answer: string;
  query_type?: string;
  processing_time?: number;
}

export interface UploadResponse {
  success: boolean;
  pdf_uuid?: string;
  filename?: string;
  display_name?: string;
  error?: string;
}

export interface ComparisonResult {
  conventional_rag: {
    success: boolean;
    answer?: string;
    processing_time?: number;
    description?: string;
    error?: string;
  };
  hybrid_rag: {
    success: boolean;
    answer?: string;
    processing_time?: number;
    query_type?: string;
    description?: string;
    error?: string;
  };
}
