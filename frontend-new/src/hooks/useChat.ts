// Custom hook for chat functionality
import { useState, useCallback, useEffect } from 'react';
import type { Message, PDFDocument } from '../types';
import { apiService } from '../services/api';
import { formatResponse, needsFormatting } from '../utils/formatResponse';
import { saveChatHistory, loadChatHistoryByHash } from '../utils/chatStorage';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentDocument, setCurrentDocument] = useState<PDFDocument | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Auto-save chat history whenever messages change
  useEffect(() => {
    if (currentDocument?.hash && messages.length > 0) {
      saveChatHistory(
        currentDocument.hash,
        {
          name: currentDocument.displayName,
          hash: currentDocument.hash,
          uuid: currentDocument.uuid,
          uploadedAt: currentDocument.uploadedAt.toISOString(),
          lastAccessedAt: new Date().toISOString(),
        },
        messages
      );
    }
  }, [messages, currentDocument]);

  /**
   * Send a message and get response
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Add user message immediately - THIS IS KEY FOR PROPER UX
      const userMessage: Message = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Add loading message
      const loadingMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, loadingMessage]);
      setIsProcessing(true);

      try {
        // Call API
        const response = await apiService.sendQuery(
          content.trim(),
          currentDocument?.uuid
        );

        let formattedAnswer = response.answer;

        // Check if response needs formatting (ugly table data, etc.)
        if (needsFormatting(response.answer)) {
          try {
            // Use backend Gemini-powered formatting for best results
            const formatted = await apiService.formatResponse(response.answer);
            formattedAnswer = formatted;
          } catch (formatError) {
            // Fallback to client-side formatting if backend fails
            console.warn('Backend formatting failed, using client-side:', formatError);
            formattedAnswer = formatResponse(response.answer);
          }
        }

        // Replace loading message with actual response
        setMessages((prev) =>
          prev.map((msg, idx) =>
            idx === prev.length - 1 && msg.isLoading
              ? {
                  role: 'assistant',
                  content: formattedAnswer,
                  timestamp: new Date(),
                  isLoading: false,
                }
              : msg
          )
        );
      } catch (error: any) {
        console.error('Error sending message:', error);

        // Replace loading message with error
        setMessages((prev) =>
          prev.map((msg, idx) =>
            idx === prev.length - 1 && msg.isLoading
              ? {
                  role: 'assistant',
                  content: error.message || 'An error occurred',
                  timestamp: new Date(),
                  isLoading: false,
                  error: true,
                }
              : msg
          )
        );
      } finally {
        setIsProcessing(false);
      }
    },
    [currentDocument]
  );

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  /**
   * Set current document and restore chat history if exists
   */
  const setDocument = useCallback((document: PDFDocument | null) => {
    setCurrentDocument(document);
    
    if (document && document.hash) {
      // Try to restore chat history for this document
      const existingHistory = loadChatHistoryByHash(document.hash);
      
      if (existingHistory && existingHistory.chatHistory.length > 0) {
        // Restore previous chat
        console.log(`📜 Restoring chat history: ${existingHistory.chatHistory.length} messages`);
        
        // Convert timestamp strings back to Date objects
        const restoredMessages = existingHistory.chatHistory.map(msg => ({
          ...msg,
          timestamp: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp
        }));
        
        setMessages(restoredMessages);
      } else {
        // No history, start fresh
        console.log(`🆕 Starting new conversation for: ${document.displayName}`);
        setMessages([]);
      }
    } else if (document) {
      // Document without hash (shouldn't happen, but fallback)
      setMessages([]);
    }
  }, []);

  return {
    messages,
    currentDocument,
    isProcessing,
    sendMessage,
    clearMessages,
    setDocument,
  };
};

