// Chat Storage Utility - LocalStorage with Content-Based Identification
import type { Message } from '../types';

// Import crypto-js but use it as fallback only
// TypeScript will bundle it, but we prefer native Web Crypto API
import CryptoJS from 'crypto-js';

const STORAGE_KEY = 'hybridrag_chat_history';
const COMPARISON_STORAGE_KEY = 'hybridrag_comparison_history';

export interface PDFChatData {
  pdfInfo: {
    name: string;
    hash: string;
    uuid: string;
    uploadedAt: string;
    lastAccessedAt: string;
  };
  chatHistory: Message[];
  comparisonHistory: ComparisonRecord[];
}

export interface ComparisonRecord {
  query: string;
  conventional: {
    answer: string;
    time: number;
  };
  hybrid: {
    answer: string;
    time: number;
    route: string;
  };
  timestamp: string;
}

export interface StorageData {
  [fileHash: string]: PDFChatData;
}

/**
 * Calculate file hash for content-based identification
 * Same file content = Same hash = Same chat history!
 * Uses Web Crypto API (native) or fallback to simple hash
 */
export const calculateFileHash = async (file: File): Promise<string> => {
  try {
    // Try using native Web Crypto API (best, works everywhere)
    if (window.crypto && window.crypto.subtle) {
      const arrayBuffer = await file.arrayBuffer();
      const hashBuffer = await window.crypto.subtle.digest('SHA-256', arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return hashHex;
    }
  } catch (cryptoError) {
    console.warn('Web Crypto API failed, trying crypto-js:', cryptoError);
  }

  // Fallback to crypto-js if available
  if (CryptoJS) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const arrayBuffer = e.target?.result as ArrayBuffer;
          const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
          const hash = CryptoJS.MD5(wordArray).toString();
          resolve(hash);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
  }

  // Final fallback: simple hash based on file properties
  // Not cryptographically secure, but good enough for history tracking
  console.warn('Using fallback file identification (name + size + modified date)');
  const simpleHash = `${file.name}-${file.size}-${file.lastModified}`;
  return btoa(simpleHash).replace(/[^a-zA-Z0-9]/g, ''); // Base64 encode and remove special chars
};

/**
 * Load all chat history from LocalStorage
 */
export const loadAllChatHistory = (): StorageData => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Error loading chat history:', error);
    return {};
  }
};

/**
 * Load chat history for a specific PDF (by hash)
 */
export const loadChatHistoryByHash = (fileHash: string): PDFChatData | null => {
  try {
    const allData = loadAllChatHistory();
    return allData[fileHash] || null;
  } catch (error) {
    console.error('Error loading chat history:', error);
    return null;
  }
};

/**
 * Save chat history for a specific PDF
 */
export const saveChatHistory = (
  fileHash: string,
  pdfInfo: PDFChatData['pdfInfo'],
  messages: Message[]
): void => {
  try {
    const allData = loadAllChatHistory();
    
    // Update or create entry
    allData[fileHash] = {
      pdfInfo: {
        ...pdfInfo,
        lastAccessedAt: new Date().toISOString(),
      },
      chatHistory: messages,
      comparisonHistory: allData[fileHash]?.comparisonHistory || [],
    };
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
  } catch (error) {
    console.error('Error saving chat history:', error);
  }
};

/**
 * Update existing comparison and move it to the top (most recent)
 * Used when "Run Again" is clicked - updates the same entry instead of creating duplicate
 */
export const updateComparison = (
  fileHash: string,
  query: string,
  updatedComparison: ComparisonRecord
): void => {
  try {
    const allData = loadAllChatHistory();
    
    if (!allData[fileHash] || !allData[fileHash].comparisonHistory) {
      console.warn('No comparison history found for this PDF hash');
      return;
    }
    
    const history = allData[fileHash].comparisonHistory;
    const queryKey = query.toLowerCase().trim();
    
    // Find the index of the existing comparison
    const existingIndex = history.findIndex(
      item => item.query.toLowerCase().trim() === queryKey
    );
    
    if (existingIndex !== -1) {
      // Remove the existing entry from its current position
      history.splice(existingIndex, 1);
      
      // Add the updated version to the end (which becomes first when reversed in display)
      history.push(updatedComparison);
      
      console.log(`✅ Updated comparison and moved to top: "${query}"`);
    } else {
      // If not found, add as new entry
      history.push(updatedComparison);
    }
    
    // Keep only last 20 comparisons per PDF
    if (history.length > 20) {
      allData[fileHash].comparisonHistory = history.slice(-20);
    }
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
  } catch (error) {
    console.error('Error updating comparison:', error);
  }
};

/**
 * Save comparison result
 */
export const saveComparison = (
  fileHash: string,
  comparison: ComparisonRecord
): void => {
  try {
    const allData = loadAllChatHistory();
    
    if (!allData[fileHash]) {
      console.warn('No chat data found for this PDF hash');
      return;
    }
    
    // Add comparison to history
    allData[fileHash].comparisonHistory.push(comparison);
    
    // Keep only last 20 comparisons per PDF
    if (allData[fileHash].comparisonHistory.length > 20) {
      allData[fileHash].comparisonHistory = allData[fileHash].comparisonHistory.slice(-20);
    }
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
  } catch (error) {
    console.error('Error saving comparison:', error);
  }
};

/**
 * Clear chat history for specific PDF
 */
export const clearPDFHistory = (fileHash: string): void => {
  try {
    const allData = loadAllChatHistory();
    delete allData[fileHash];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
  } catch (error) {
    console.error('Error clearing PDF history:', error);
  }
};

/**
 * Clear all chat history
 */
export const clearAllHistory = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(COMPARISON_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing all history:', error);
  }
};

/**
 * Get storage statistics
 */
export const getStorageStats = () => {
  try {
    const allData = loadAllChatHistory();
    const pdfCount = Object.keys(allData).length;
    
    let totalMessages = 0;
    let totalComparisons = 0;
    
    Object.values(allData).forEach(data => {
      totalMessages += data.chatHistory.length;
      totalComparisons += data.comparisonHistory.length;
    });
    
    // Calculate storage size
    const dataStr = JSON.stringify(allData);
    const sizeInBytes = new Blob([dataStr]).size;
    const sizeInKB = (sizeInBytes / 1024).toFixed(2);
    
    return {
      pdfCount,
      totalMessages,
      totalComparisons,
      sizeInKB,
      recentPDFs: Object.entries(allData)
        .map(([hash, data]) => ({
          hash,
          name: data.pdfInfo.name,
          messageCount: data.chatHistory.length,
          lastAccessed: data.pdfInfo.lastAccessedAt,
        }))
        .sort((a, b) => 
          new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime()
        )
        .slice(0, 5),
    };
  } catch (error) {
    console.error('Error getting storage stats:', error);
    return null;
  }
};

/**
 * Export chat history as JSON
 */
export const exportChatHistory = (fileHash: string): string => {
  const data = loadChatHistoryByHash(fileHash);
  if (!data) return '';
  
  return JSON.stringify(data, null, 2);
};

/**
 * Export chat history as plain text
 */
export const exportChatAsText = (fileHash: string): string => {
  const data = loadChatHistoryByHash(fileHash);
  if (!data) return '';
  
  let text = `Chat History: ${data.pdfInfo.name}\n`;
  text += `Date: ${new Date(data.pdfInfo.uploadedAt).toLocaleString()}\n`;
  text += `\n${'='.repeat(60)}\n\n`;
  
  data.chatHistory.forEach((msg) => {
    const role = msg.role === 'user' ? 'You' : 'Assistant';
    const time = new Date(msg.timestamp).toLocaleTimeString();
    text += `[${time}] ${role}:\n${msg.content}\n\n`;
  });
  
  return text;
};

