// ChatWindow component - main chat interface
import React, { useRef, useEffect } from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import { Delete } from '@mui/icons-material';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import type { Message } from '../../types';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onClearChat: () => void;
  isProcessing: boolean;
  hasDocument: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  onClearChat,
  isProcessing,
  hasDocument,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          p: 2,
          boxShadow: 2,
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Box>
              <Typography variant="h5" fontWeight={700}>
                🧠 Hybrid RAG Assistant
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Intelligent document querying with text and table understanding
              </Typography>
            </Box>
            {messages.length > 0 && (
              <Button
                variant="outlined"
                startIcon={<Delete />}
                onClick={onClearChat}
                sx={{
                  color: 'white',
                  borderColor: 'white',
                  '&:hover': {
                    borderColor: 'white',
                    bgcolor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                Clear Chat
              </Button>
            )}
          </Box>
        </Container>
      </Box>

      {/* Messages Area - Scrollable with proper padding */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 3,
          pb: 2,
          bgcolor: 'background.default',
        }}
      >
        <Container maxWidth="lg">
          {!hasDocument ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '60vh',
                textAlign: 'center',
              }}
            >
              <Typography variant="h1" sx={{ fontSize: '5rem', mb: 2 }}>
                📚
              </Typography>
              <Typography variant="h4" color="text.primary" gutterBottom>
                No Document Loaded
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
                Upload a PDF using the sidebar to unlock the power of Hybrid RAG and start asking
                intelligent questions!
              </Typography>
              <Box
                sx={{
                  mt: 3,
                  bgcolor: 'warning.light',
                  color: 'warning.dark',
                  px: 3,
                  py: 1.5,
                  borderRadius: 2,
                  fontWeight: 600,
                }}
              >
                👈 Check out the sidebar to get started
              </Box>
            </Box>
          ) : messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '60vh',
                textAlign: 'center',
              }}
            >
              <Typography variant="h1" sx={{ fontSize: '4rem', mb: 2 }}>
                💬
              </Typography>
              <Typography variant="h5" color="text.primary" gutterBottom>
                Start a Conversation
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Ask questions about your document below!
              </Typography>
            </Box>
          ) : (
            <Box>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Container>
      </Box>

      {/* Input Area - Fixed at bottom, always visible */}
      <Box
        sx={{
          p: 2,
          pb: 3,
          bgcolor: 'background.paper',
          borderTop: 2,
          borderColor: 'primary.main',
          boxShadow: '0 -2px 10px rgba(0,0,0,0.1)',
          flexShrink: 0,
        }}
      >
        <Container maxWidth="lg">
          <ChatInput
            onSendMessage={onSendMessage}
            disabled={isProcessing || !hasDocument}
            placeholder={
              hasDocument
                ? '💭 Ask me anything about your documents...'
                : '📄 Please upload a document first'
            }
          />
        </Container>
      </Box>
    </Box>
  );
};

export default ChatWindow;

