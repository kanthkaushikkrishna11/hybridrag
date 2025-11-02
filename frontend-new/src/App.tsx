// Main App component - Simple and clean
import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, Snackbar, Alert, ToggleButton, ToggleButtonGroup, Container, Paper } from '@mui/material';
import { Chat, CompareArrows } from '@mui/icons-material';
import Sidebar from './components/Layout/Sidebar';
import ChatWindow from './components/Chat/ChatWindow';
import ComparisonDemo from './components/Comparison/ComparisonDemo';
import { useChat } from './hooks/useChat';
import type { PDFDocument } from './types';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#667eea',
      dark: '#5568d3',
      light: '#7e92f2',
    },
    secondary: {
      main: '#764ba2',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    success: {
      light: '#d1fae5',
      main: '#10b981',
      dark: '#065f46',
    },
    error: {
      light: '#fee2e2',
      main: '#ef4444',
      dark: '#991b1b',
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    h5: { fontWeight: 700 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
  },
});

const DRAWER_WIDTH = 360;

type AppMode = 'chat' | 'comparison';

function App() {
  const { messages, currentDocument, isProcessing, sendMessage, clearMessages, setDocument } = useChat();
  const [mode, setMode] = useState<AppMode>('chat');
  
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleUploadSuccess = (document: PDFDocument) => {
    setDocument(document);
    setSnackbar({
      open: true,
      message: `✅ Successfully uploaded: ${document.displayName}`,
      severity: 'success',
    });
  };

  const handleUploadError = (error: string) => {
    setSnackbar({
      open: true,
      message: `❌ ${error}`,
      severity: 'error',
    });
  };

  const handleModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: AppMode | null) => {
    if (newMode !== null) {
      setMode(newMode);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Sidebar
          currentDocument={currentDocument}
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: `calc(100% - ${DRAWER_WIDTH}px)`,
            height: '100vh',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Mode Selector - Only show when document is loaded */}
          {currentDocument && (
            <Box
              sx={{
                bgcolor: 'background.paper',
                borderBottom: 1,
                borderColor: 'divider',
                py: 2,
              }}
            >
              <Container maxWidth="lg">
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Paper elevation={2} sx={{ p: 0.5, borderRadius: 2 }}>
                    <ToggleButtonGroup
                      value={mode}
                      exclusive
                      onChange={handleModeChange}
                      aria-label="app mode"
                      sx={{
                        '& .MuiToggleButton-root': {
                          px: 3,
                          py: 1,
                          textTransform: 'none',
                          fontWeight: 600,
                          fontSize: '1rem',
                        },
                      }}
                    >
                      <ToggleButton value="chat" aria-label="normal chat">
                        <Chat sx={{ mr: 1 }} />
                        💬 Normal Chat
                      </ToggleButton>
                      <ToggleButton value="comparison" aria-label="comparison demo">
                        <CompareArrows sx={{ mr: 1 }} />
                        🔍 Comparison Demo
                      </ToggleButton>
                    </ToggleButtonGroup>
                  </Paper>
                </Box>
              </Container>
            </Box>
          )}

          {/* Main Content Area - Keep both components mounted */}
          <Box sx={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
            {/* Normal Chat - shown when mode === 'chat' */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: mode === 'chat' ? 'flex' : 'none',
                flexDirection: 'column',
              }}
            >
              <ChatWindow
                messages={messages}
                onSendMessage={sendMessage}
                onClearChat={clearMessages}
                isProcessing={isProcessing}
                hasDocument={currentDocument !== null}
              />
            </Box>

            {/* Comparison Demo - shown when mode === 'comparison' */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: mode === 'comparison' ? 'flex' : 'none',
                flexDirection: 'column',
              }}
            >
          <ComparisonDemo
            pdfUuid={currentDocument?.uuid || null}
            pdfName={currentDocument?.displayName || null}
            pdfHash={currentDocument?.hash || null}
          />
            </Box>
          </Box>
        </Box>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={3500}
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          sx={{
            top: '80px !important',
            maxWidth: '600px',
          }}
        >
          <Alert
            onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
            severity={snackbar.severity}
            variant="filled"
            sx={{
              width: '100%',
              boxShadow: 4,
            }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;
