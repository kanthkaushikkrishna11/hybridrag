// Simple FileUploader component
import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import { CloudUpload, InsertDriveFile, CheckCircle, History } from '@mui/icons-material';
import { apiService } from '../../services/api';
import type { PDFDocument } from '../../types';
import { calculateFileHash, loadChatHistoryByHash } from '../../utils/chatStorage';

interface FileUploaderProps {
  currentDocument: PDFDocument | null;
  onUploadSuccess: (document: PDFDocument) => void;
  onUploadError: (error: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  currentDocument,
  onUploadSuccess,
  onUploadError,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyInfo, setHistoryInfo] = useState<{ exists: boolean; messageCount: number } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    setError(null);
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file');
      return false;
    }

    const maxSize = 20 * 1024 * 1024; // 20MB
    if (file.size > maxSize) {
      setError(`File too large. Max size is 20MB. Your file: ${(file.size / (1024 * 1024)).toFixed(1)}MB`);
      return false;
    }

    if (file.size === 0) {
      setError('File is empty');
      return false;
    }

    return true;
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      
      // Check if history exists for this file
      try {
        const fileHash = await calculateFileHash(file);
        const existingHistory = loadChatHistoryByHash(fileHash);
        
        if (existingHistory && existingHistory.chatHistory.length > 0) {
          setHistoryInfo({
            exists: true,
            messageCount: existingHistory.chatHistory.length,
          });
        } else {
          setHistoryInfo({ exists: false, messageCount: 0 });
        }
      } catch (error) {
        console.error('Error checking file history:', error);
        setHistoryInfo(null);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      
      // Check if history exists for this file
      try {
        const fileHash = await calculateFileHash(file);
        const existingHistory = loadChatHistoryByHash(fileHash);
        
        if (existingHistory && existingHistory.chatHistory.length > 0) {
          setHistoryInfo({
            exists: true,
            messageCount: existingHistory.chatHistory.length,
          });
        } else {
          setHistoryInfo({ exists: false, messageCount: 0 });
        }
      } catch (error) {
        console.error('Error checking file history:', error);
        setHistoryInfo(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 10, 90));
    }, 500);

    try {
      // Calculate file hash for content-based identification
      const fileHash = await calculateFileHash(selectedFile);
      
      const result = await apiService.uploadPDF(selectedFile);
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (result.success && result.pdf_uuid) {
        const document: PDFDocument = {
          uuid: result.pdf_uuid,
          name: result.filename || selectedFile.name,
          displayName: result.display_name || result.filename || selectedFile.name,
          uploadedAt: new Date(),
          hash: fileHash,  // Add file hash for history tracking
        };
        
        onUploadSuccess(document);
        setSelectedFile(null);
        setHistoryInfo(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (err: any) {
      clearInterval(progressInterval);
      const errorMsg = err.message || 'Upload failed. Please try again.';
      setError(errorMsg);
      onUploadError(errorMsg);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        📄 Document Upload
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {currentDocument && !uploading && (
        <Paper elevation={2} sx={{ p: 2, mb: 2, bgcolor: 'success.light', color: 'success.dark' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <CheckCircle fontSize="small" />
            <Typography variant="subtitle2" fontWeight={600}>Active Document</Typography>
          </Box>
          <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>
            {currentDocument.displayName}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            Uploaded: {currentDocument.uploadedAt.toLocaleString()}
          </Typography>
        </Paper>
      )}

      <Paper
        elevation={1}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        sx={{
          p: 3,
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          border: 2,
          borderStyle: 'dashed',
          borderColor: isDragging ? 'primary.main' : 'divider',
          bgcolor: isDragging ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s',
          opacity: uploading ? 0.6 : 1,
          '&:hover': {
            borderColor: uploading ? 'divider' : 'primary.main',
            bgcolor: uploading ? 'background.paper' : 'action.hover',
          },
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
          disabled={uploading}
        />

        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="body1" fontWeight={600} gutterBottom>
          {selectedFile ? 'File Selected' : 'Choose a PDF file'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Drag and drop or click to browse
        </Typography>
        <Chip label="Limit: 20MB" size="small" sx={{ mt: 1 }} />
      </Paper>

      {selectedFile && !uploading && (
        <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <InsertDriveFile color="primary" />
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="body2" fontWeight={600} sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {selectedFile.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </Typography>
            </Box>
          </Box>
          
          {/* History notification */}
          {historyInfo?.exists && (
            <Alert severity="info" icon={<History />} sx={{ mb: 2, py: 0.5 }}>
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                📜 Chat history found ({historyInfo.messageCount} messages)
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem', opacity: 0.8 }}>
                Your previous conversation will be restored
              </Typography>
            </Alert>
          )}
          
          <Button
            fullWidth
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={handleUpload}
            disabled={uploading}
            sx={{ mt: 1 }}
          >
            Upload & Process
          </Button>
        </Paper>
      )}

      {uploading && (
        <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            Uploading Document...
          </Typography>
          <LinearProgress variant="determinate" value={uploadProgress} sx={{ mb: 1 }} />
          <Typography variant="caption" color="text.secondary">
            {uploadProgress < 100 ? `Processing: ${uploadProgress}%` : 'Finalizing...'}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default FileUploader;
