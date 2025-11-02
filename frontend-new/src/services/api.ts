// API service for backend communication
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for regular requests
});

export const apiService = {
  async uploadPDF(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/uploadpdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000, // 10 minutes for PDF uploads (t3.micro is slow)
    });
    
    return response.data;
  },

  async sendQuery(query: string, pdfUuid?: string) {
    const response = await apiClient.post('/answer', {
      query,
      pdf_uuid: pdfUuid,
    });
    return response.data;
  },

  async getComparison(query: string, pdfUuid: string) {
    const response = await apiClient.post('/compare', {
      query,
      pdf_uuid: pdfUuid,
    });
    return response.data;
  },

  async formatResponse(rawAnswer: string): Promise<string> {
    try {
      const response = await apiClient.post('/format_response', {
        raw_answer: rawAnswer,
      });
      
      if (response.data.success && response.data.formatted_answer) {
        return response.data.formatted_answer;
      }
      
      // If formatting failed, return original
      return rawAnswer;
    } catch (error) {
      console.error('Error formatting response:', error);
      // Return original on error
      return rawAnswer;
    }
  },
};

export default apiService;
