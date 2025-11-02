// ChatInput component - input field for user messages
import React, { useState, useRef } from 'react';
import type { KeyboardEvent } from 'react';
import { Box, IconButton, Paper } from '@mui/material';
import { Send } from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = '💭 Ask me anything about your documents...',
}) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue && !disabled) {
      onSendMessage(trimmedValue);
      setInputValue('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modifierKey = isMac ? event.metaKey : event.ctrlKey;

    // Handle Enter key for sending message
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
      return;
    }

    // EXPLICITLY handle keyboard shortcuts to ensure they work
    if (modifierKey) {
      const textarea = event.currentTarget;
      
      switch (event.key.toLowerCase()) {
        case 'a': // Select All
          event.preventDefault();
          textarea.select();
          console.log('✅ Cmd+A: Select All executed');
          break;
          
        case 'x': // Cut
          event.preventDefault();
          const cutText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
          if (cutText) {
            // Use clipboard API only if available (HTTPS/localhost)
            if (navigator.clipboard && navigator.clipboard.writeText) {
              navigator.clipboard.writeText(cutText).then(() => {
                console.log('✅ Cmd+X: Cut executed (clipboard)');
              }).catch(() => {
                console.log('⚠️ Clipboard write failed, but cut executed');
              });
            }
            // Execute cut regardless of clipboard API
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const newValue = textarea.value.substring(0, start) + textarea.value.substring(end);
            setInputValue(newValue);
            // Set cursor position
            setTimeout(() => {
              textarea.selectionStart = start;
              textarea.selectionEnd = start;
            }, 0);
          }
          break;
          
        case 'c': // Copy
          event.preventDefault();
          const copyText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
          if (copyText && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(copyText).then(() => {
              console.log('✅ Cmd+C: Copy executed');
            }).catch(() => {
              console.log('⚠️ Clipboard API not available (HTTP)');
            });
          }
          break;
          
        case 'v': // Paste
          // Don't prevent default - let browser handle paste on HTTP sites
          if (navigator.clipboard && navigator.clipboard.readText) {
            event.preventDefault();
            navigator.clipboard.readText().then(text => {
              const start = textarea.selectionStart;
              const end = textarea.selectionEnd;
              const newValue = textarea.value.substring(0, start) + text + textarea.value.substring(end);
              setInputValue(newValue);
              // Set cursor position after pasted text
              setTimeout(() => {
                const newCursorPos = start + text.length;
                textarea.selectionStart = newCursorPos;
                textarea.selectionEnd = newCursorPos;
              }, 0);
              console.log('✅ Cmd+V: Paste executed (clipboard API)');
            }).catch(() => {
              console.log('⚠️ Clipboard read failed, using browser paste');
            });
          } else {
            // Let browser handle paste naturally on HTTP
            console.log('⚠️ Clipboard API not available, using browser paste');
          }
          break;
          
        case 'z': // Undo (let native behavior handle this)
          // Don't prevent default - let browser handle undo
          console.log('✅ Cmd+Z: Undo (native)');
          break;
      }
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
    
    // Auto-resize textarea
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        borderRadius: 2,
        bgcolor: 'background.paper',
      }}
    >
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        {/* Native textarea with Material-UI styling */}
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          style={{
            width: '100%',
            minHeight: '56px',
            maxHeight: '120px',
            padding: '16.5px 14px',
            fontSize: '1rem',
            fontFamily: 'inherit',
            lineHeight: 1.5,
            border: '1px solid rgba(0, 0, 0, 0.23)',
            borderRadius: '8px',
            outline: 'none',
            resize: 'none',
            backgroundColor: disabled ? '#f5f5f5' : 'white',
            color: disabled ? 'rgba(0, 0, 0, 0.38)' : 'inherit',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = '#1976d2';
            e.target.style.borderWidth = '2px';
            e.target.style.padding = '15.5px 13px';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'rgba(0, 0, 0, 0.23)';
            e.target.style.borderWidth = '1px';
            e.target.style.padding = '16.5px 14px';
          }}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={disabled || !inputValue.trim()}
          sx={{
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            '&.Mui-disabled': {
              bgcolor: 'action.disabledBackground',
            },
            width: 48,
            height: 48,
          }}
        >
          <Send />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatInput;

