// Separate PDF-related types to avoid module resolution issues

export interface PDFDocument {
  uuid: string;
  name: string;
  displayName: string;
  uploadedAt: Date;
}

export interface UploadResponse {
  success: boolean;
  pdf_uuid?: string;
  filename?: string;
  pdf_name?: string;
  display_name?: string;
  error?: string;
  message?: string;
}

