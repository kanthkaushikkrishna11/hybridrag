// ChatMessage component - displays individual chat messages
import React from 'react';
import { Box, Paper, Typography, CircularProgress, Avatar, Alert } from '@mui/material';
import { Person, SmartToy } from '@mui/icons-material';
import type { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        alignItems: 'flex-start',
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            bgcolor: 'secondary.main',
            mr: 1,
            width: 36,
            height: 36,
          }}
        >
          <SmartToy fontSize="small" />
        </Avatar>
      )}

      <Paper
        elevation={2}
        sx={{
          p: 2,
          maxWidth: '70%',
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderRadius: 2,
        }}
      >
        {message.isLoading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={16} color="inherit" />
            <Typography variant="body2">Thinking...</Typography>
          </Box>
        ) : message.error ? (
          <Typography variant="body1" color="error">
            ❌ I'm sorry, I encountered an error while processing your question. Please try again.
          </Typography>
        ) : message.content.includes('QUOTA EXCEEDED') ? (
          <Alert severity="warning" icon="⚠️" sx={{ 
            bgcolor: 'warning.light', 
            border: '2px solid',
            borderColor: 'warning.main'
          }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
              ⚠️ GEMINI API QUOTA EXCEEDED
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.9rem' }}>
              The daily API request limit has been reached. Please try again later.
            </Typography>
            <Typography variant="caption" component="div" sx={{ mt: 1, opacity: 0.8 }}>
              Free tier: 250 requests/day | Resets at midnight UTC
            </Typography>
          </Alert>
        ) : (
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {formatMessageContent(message.content)}
          </Typography>
        )}

        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 1,
            opacity: 0.7,
            fontSize: '0.7rem',
          }}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      </Paper>

      {isUser && (
        <Avatar
          sx={{
            bgcolor: 'primary.main',
            ml: 1,
            width: 36,
            height: 36,
          }}
        >
          <Person fontSize="small" />
        </Avatar>
      )}
    </Box>
  );
};

/**
 * Formats message content for display
 * Handles bullet points, line breaks, etc.
 */
function formatMessageContent(content: string): React.ReactNode {
  if (!content) return '';

  // Split by lines
  const lines = content.split('\n');
  
  return lines.map((line, index) => {
    // Check if line is a bullet point
    if (line.trim().startsWith('•')) {
      return (
        <Box key={index} sx={{ pl: 2, my: 0.5 }}>
          {line}
        </Box>
      );
    }
    
    // Check if line contains bold markdown (**text**)
    if (line.includes('**')) {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <span key={index}>
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={i}>{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
          {index < lines.length - 1 && <br />}
        </span>
      );
    }
    
    // Regular line
    return (
      <React.Fragment key={index}>
        {line}
        {index < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
}

export default ChatMessage;

