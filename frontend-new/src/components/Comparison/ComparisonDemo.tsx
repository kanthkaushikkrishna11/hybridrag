// ComparisonDemo component - Compare Conventional RAG vs Hybrid RAG
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Card,
  CardContent,
  Divider,
  Snackbar,
} from '@mui/material';
import { PlayArrow, History as HistoryIcon, Refresh } from '@mui/icons-material';
import { apiService } from '../../services/api';
import type { ComparisonResult } from '../../types';
import { saveComparison, loadChatHistoryByHash, updateComparison } from '../../utils/chatStorage';

interface ComparisonDemoProps {
  pdfUuid: string | null;
  pdfName: string | null;
  pdfHash?: string | null;
}

const ComparisonDemo: React.FC<ComparisonDemoProps> = ({ pdfUuid, pdfName, pdfHash }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [comparisonHistory, setComparisonHistory] = useState<any[]>([]);
  const [cleanupMessage, setCleanupMessage] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  // Track component mount status for cleanup
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Load comparison history when PDF changes
  useEffect(() => {
    if (pdfHash) {
      const historyData = loadChatHistoryByHash(pdfHash);
      if (historyData && historyData.comparisonHistory) {
        // Show most recent first
        setComparisonHistory([...historyData.comparisonHistory].reverse());
      } else {
        setComparisonHistory([]);
      }
    } else {
      setComparisonHistory([]);
    }
  }, [pdfHash]);

  const suggestedQuestions = [
    { label: '📊 Table Query', question: 'What are the names of teams that won Final matches?' },
    { label: '📝 Text Query', question: 'What is the historical significance of the FIFA World Cup and when did it start?' },
    { label: '🔀 Hybrid Query', question: 'Provide a comprehensive overview of Uruguays World Cup journey including their match statistics and historical achievements' },
  ];

  const handleRunComparison = async () => {
    if (!query.trim()) {
      setError('Please enter a question first!');
      return;
    }

    if (!pdfUuid) {
      setError('Please upload a PDF document first!');
      return;
    }

    // Check if this exact query was already run
    const duplicateComparison = comparisonHistory.find(
      item => item.query.toLowerCase().trim() === query.toLowerCase().trim()
    );
    
    if (duplicateComparison) {
      setError(
        `⚠️ This question was already compared! See result #${comparisonHistory.indexOf(duplicateComparison) + 1} in the history below. ` +
        `(Run at: ${new Date(duplicateComparison.timestamp).toLocaleString()})`
      );
      // Scroll to history section
      setTimeout(() => {
        document.getElementById('comparison-history')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 500);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiService.getComparison(query, pdfUuid);
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setResult(data);
        
        // Save comparison to history if we have a document hash
        // BUT only if it's not a duplicate!
        if (pdfHash) {
          // Check if this query already exists in history
          const existingHistory = loadChatHistoryByHash(pdfHash);
          const isDuplicate = existingHistory?.comparisonHistory?.some(
            item => item.query.toLowerCase().trim() === query.toLowerCase().trim()
          );
          
          if (!isDuplicate) {
            // Only save if NOT a duplicate
            saveComparison(pdfHash, {
              query,
              conventional: {
                answer: data.conventional_rag.answer || '',
                time: data.conventional_rag.processing_time || 0,
              },
              hybrid: {
                answer: data.hybrid_rag.answer || '',
                time: data.hybrid_rag.processing_time || 0,
                route: data.hybrid_rag.query_type || 'unknown',
              },
              timestamp: new Date().toISOString(),
            });
            
            // Reload comparison history to show the new comparison
            const historyData = loadChatHistoryByHash(pdfHash);
            if (historyData && historyData.comparisonHistory) {
              setComparisonHistory([...historyData.comparisonHistory].reverse());
            }
          }
        }
      }
    } catch (err: any) {
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setError(err.response?.data?.error || err.message || 'Failed to run comparison');
      }
    } finally {
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setQuery(question);
  };

  const handleRemoveDuplicates = () => {
    if (!pdfHash) {
      setCleanupMessage('⚠️ No document loaded');
      return;
    }

    const historyData = loadChatHistoryByHash(pdfHash);
    if (!historyData || !historyData.comparisonHistory) {
      setCleanupMessage('⚠️ No history to clean');
      return;
    }

    const seen = new Set<string>();
    const unique: any[] = [];
    let duplicatesRemoved = 0;

    // Keep only first occurrence of each unique query
    historyData.comparisonHistory.forEach((item: any) => {
      const queryKey = item.query.toLowerCase().trim();
      if (!seen.has(queryKey)) {
        seen.add(queryKey);
        unique.push(item);
      } else {
        duplicatesRemoved++;
      }
    });

    if (duplicatesRemoved === 0) {
      setCleanupMessage('✅ No duplicates found!');
      return;
    }

    // Update history data
    historyData.comparisonHistory = unique;

    // Save back to localStorage
    const allData = JSON.parse(localStorage.getItem('hybridrag_chat_history') || '{}');
    allData[pdfHash] = historyData;
    localStorage.setItem('hybridrag_chat_history', JSON.stringify(allData));

    // Reload comparison history
    setComparisonHistory([...unique].reverse());

    setCleanupMessage(`🧹 Removed ${duplicatesRemoved} duplicate${duplicatesRemoved !== 1 ? 's' : ''}!`);
  };

  const handleRunAgain = async (queryToRun: string) => {
    if (!pdfUuid) {
      setError('Please upload a PDF document first!');
      return;
    }

    // Set the query in the input field
    setQuery(queryToRun);

    // Set loading state
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiService.getComparison(queryToRun, pdfUuid);
      
      if (isMountedRef.current) {
        setResult(data);
        
        // Update existing comparison entry instead of creating new one
        // This moves the updated entry to the top (most recent)
        if (pdfHash) {
          updateComparison(pdfHash, queryToRun, {
            query: queryToRun,
            conventional: {
              answer: data.conventional_rag.answer || '',
              time: data.conventional_rag.processing_time || 0,
            },
            hybrid: {
              answer: data.hybrid_rag.answer || '',
              time: data.hybrid_rag.processing_time || 0,
              route: data.hybrid_rag.query_type || 'unknown',
            },
            timestamp: new Date().toISOString(),
          });
          
          // Reload comparison history to show the updated entry at top
          const historyData = loadChatHistoryByHash(pdfHash);
          if (historyData && historyData.comparisonHistory) {
            setComparisonHistory([...historyData.comparisonHistory].reverse());
          }
        }
        
        // Scroll to top to show the updated result
        setTimeout(() => {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 100);
      }
    } catch (err: any) {
      if (isMountedRef.current) {
        setError(err.response?.data?.error || err.message || 'Failed to run comparison');
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  if (!pdfUuid) {
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
            <Typography variant="h5" fontWeight={700}>
              🎯 Comparison Demo
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Compare Conventional RAG vs Hybrid RAG
            </Typography>
          </Container>
        </Box>

        {/* No document loaded */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <Card
            sx={{
              maxWidth: 600,
              textAlign: 'center',
              p: 4,
              background: 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
            }}
          >
            <Typography variant="h1" sx={{ fontSize: '4rem', mb: 2 }}>
              ⚠️
            </Typography>
            <Typography variant="h5" color="error.dark" gutterBottom fontWeight={600}>
              Upload Required
            </Typography>
            <Typography variant="body1" color="error.dark" sx={{ mt: 2 }}>
              Please upload a PDF document first to try the comparison demo!
            </Typography>
            <Typography variant="body2" color="error.dark" sx={{ mt: 2, opacity: 0.9 }}>
              💡 Upload a PDF with tables (like the FIFA World Cup PDF) for best results.
            </Typography>
          </Card>
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: 'background.default',
        overflow: 'hidden',
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
          <Typography variant="h5" fontWeight={700}>
            🎯 Comparison Demo
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Compare Conventional RAG vs Hybrid RAG
          </Typography>
        </Container>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
        <Container maxWidth="lg">
          {/* Active Document */}
          <Card
            sx={{
              mb: 3,
              background: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
              color: 'white',
            }}
          >
            <CardContent sx={{ display: 'flex', alignItems: 'center', py: 2 }}>
              <Typography variant="h4" sx={{ mr: 2 }}>
                📄
              </Typography>
              <Box>
                <Typography variant="caption" sx={{ opacity: 0.9, display: 'block' }}>
                  LOADED DOCUMENT
                </Typography>
                <Typography variant="h6" fontWeight={600}>
                  {pdfName}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Introduction */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              🎯 Comparison Demo
            </Typography>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Conventional RAG vs Hybrid RAG
            </Typography>
          </Box>

          {/* Explanation */}
          <Paper sx={{ p: 3, mb: 3, bgcolor: 'grey.50' }}>
            <Typography variant="body1" color="text.primary" sx={{ lineHeight: 1.6 }}>
              This demo shows the <strong>difference</strong> between:
              <br />
              <br />
              📚 <strong>Conventional RAG:</strong> Uses only vector search on text embeddings (Pinecone)
              <br />
              🧠 <strong>Hybrid RAG:</strong> Uses LangGraph to intelligently route queries to text,
              tables, or both
            </Typography>
          </Paper>

          <Divider sx={{ my: 3 }} />

          {/* Query Input */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              🔍 Enter your question:
            </Typography>
            {/* Native textarea with EXPLICIT keyboard shortcut handling */}
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(event) => {
                const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
                const modifierKey = isMac ? event.metaKey : event.ctrlKey;

                // EXPLICITLY handle keyboard shortcuts
                if (modifierKey) {
                  const textarea = event.currentTarget;
                  
                  switch (event.key.toLowerCase()) {
                    case 'a': // Select All
                      event.preventDefault();
                      textarea.select();
                      console.log('✅ Comparison: Cmd+A executed');
                      break;
                      
                    case 'x': // Cut
                      event.preventDefault();
                      const cutText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
                      if (cutText) {
                        navigator.clipboard.writeText(cutText).then(() => {
                          const start = textarea.selectionStart;
                          const end = textarea.selectionEnd;
                          const newValue = textarea.value.substring(0, start) + textarea.value.substring(end);
                          setQuery(newValue);
                          setTimeout(() => {
                            textarea.selectionStart = start;
                            textarea.selectionEnd = start;
                          }, 0);
                          console.log('✅ Comparison: Cmd+X executed');
                        });
                      }
                      break;
                      
                    case 'c': // Copy
                      event.preventDefault();
                      const copyText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
                      if (copyText) {
                        navigator.clipboard.writeText(copyText).then(() => {
                          console.log('✅ Comparison: Cmd+C executed');
                        });
                      }
                      break;
                      
                    case 'v': // Paste
                      event.preventDefault();
                      navigator.clipboard.readText().then(text => {
                        const start = textarea.selectionStart;
                        const end = textarea.selectionEnd;
                        const newValue = textarea.value.substring(0, start) + text + textarea.value.substring(end);
                        setQuery(newValue);
                        setTimeout(() => {
                          const newCursorPos = start + text.length;
                          textarea.selectionStart = newCursorPos;
                          textarea.selectionEnd = newCursorPos;
                        }, 0);
                        console.log('✅ Comparison: Cmd+V executed');
                      });
                      break;
                  }
                }
              }}
              placeholder="e.g., What is the historical significance of the FIFA World Cup?"
              disabled={loading}
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '16.5px 14px',
                fontSize: '1rem',
                fontFamily: 'inherit',
                lineHeight: 1.5,
                border: '1px solid rgba(0, 0, 0, 0.23)',
                borderRadius: '4px',
                outline: 'none',
                resize: 'vertical',
                backgroundColor: loading ? '#f5f5f5' : 'white',
                color: loading ? 'rgba(0, 0, 0, 0.38)' : 'inherit',
                transition: 'border-color 0.2s',
                marginBottom: '16px',
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

            {/* Suggested Questions */}
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              💡 Try These Questions:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              {suggestedQuestions.map((sq, idx) => (
                <Chip
                  key={idx}
                  label={sq.label}
                  onClick={() => handleSuggestedQuestion(sq.question)}
                  clickable
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>

            {/* Run Button */}
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
              onClick={handleRunComparison}
              disabled={loading || !query.trim()}
              sx={{
                py: 1.5,
                fontSize: '1.1rem',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              }}
            >
              {loading ? 'Running Comparison...' : '🚀 Run Comparison'}
            </Button>
          </Box>

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Quota Exceeded Warning - Show prominently if detected */}
          {result && (result.hybrid_rag?.error === 'QUOTA_EXCEEDED' || result.conventional_rag?.error === 'QUOTA_EXCEEDED' || 
           result.hybrid_rag?.answer?.includes('QUOTA EXCEEDED') || result.conventional_rag?.answer?.includes('QUOTA EXCEEDED')) && (
            <Alert severity="warning" icon="⚠️" sx={{ mb: 3, fontSize: '1.1rem', fontWeight: 600 }}>
              <Typography variant="h6" sx={{ mb: 1, fontWeight: 700 }}>
                ⚠️ GEMINI API QUOTA EXCEEDED
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                The daily API request limit has been reached. Please try again later.
              </Typography>
              <Typography variant="caption" component="div">
                • Free tier limit: 250 requests/day<br/>
                • Quota typically resets at midnight UTC<br/>
                • Consider waiting or using a different API key
              </Typography>
            </Alert>
          )}

          {/* Results Display - Clean Side-by-Side */}
          {result && (
            <>
              {/* Question */}
              <Paper
                elevation={2}
                sx={{
                  mb: 3,
                  p: 2,
                  bgcolor: 'grey.50',
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                }}
              >
                <Typography variant="caption" fontWeight={600} color="text.secondary" textTransform="uppercase">
                  Your Question
                </Typography>
                <Typography variant="h6" fontWeight={600} color="text.primary" sx={{ mt: 0.5 }}>
                  {query}
                </Typography>
              </Paper>

              {/* Side-by-Side Answers */}
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                {/* Conventional RAG Answer */}
                <Box sx={{ flex: '1 1 calc(50% - 12px)', minWidth: '300px' }}>
                  <Paper
                    elevation={3}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      border: '2px solid #f093fb',
                    }}
                  >
                    {/* Header */}
                    <Box
                      sx={{
                        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        color: 'white',
                        py: 2,
                        px: 3,
                        textAlign: 'center',
                      }}
                    >
                      <Typography variant="h6" fontWeight={700}>
                        📚 Conventional RAG
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Vector Search Only • {result.conventional_rag.success && result.conventional_rag.processing_time && `${result.conventional_rag.processing_time.toFixed(1)}s`}
                      </Typography>
                    </Box>

                    {/* Answer Content */}
                    <Box sx={{ p: 3, flex: 1, bgcolor: 'white' }}>
                      {result.conventional_rag.success ? (
                        <Typography variant="body1" sx={{ lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
                          {result.conventional_rag.answer}
                        </Typography>
                      ) : (
                        <Alert severity="error">
                          ❌ {result.conventional_rag.error || 'Error occurred'}
                        </Alert>
                      )}
                    </Box>
                  </Paper>
                </Box>

                {/* Hybrid RAG Answer */}
                <Box sx={{ flex: '1 1 calc(50% - 12px)', minWidth: '300px' }}>
                  <Paper
                    elevation={3}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      border: '2px solid #4facfe',
                    }}
                  >
                    {/* Header */}
                    <Box
                      sx={{
                        background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                        color: 'white',
                        py: 2,
                        px: 3,
                        textAlign: 'center',
                      }}
                    >
                      <Typography variant="h6" fontWeight={700}>
                        🧠 Hybrid RAG
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        LangGraph + Tables • {result.hybrid_rag.success && result.hybrid_rag.processing_time && `${result.hybrid_rag.processing_time.toFixed(1)}s`}
                      </Typography>
                    </Box>

                    {/* Answer Content */}
                    <Box sx={{ p: 3, flex: 1, bgcolor: 'white' }}>
                      {result.hybrid_rag.success ? (
                        <Typography variant="body1" sx={{ lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
                          {result.hybrid_rag.answer}
                        </Typography>
                      ) : (
                        <Alert severity="error">
                          ❌ {result.hybrid_rag.error || 'Error occurred'}
                        </Alert>
                      )}
                    </Box>
                  </Paper>
                </Box>
              </Box>

              {/* Simple Footer Note */}
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1rem', fontWeight: 500 }}>
                  <strong>Note:</strong> Conventional RAG uses vector search (faster, may miss table data) • Hybrid RAG uses intelligent routing (more accurate with structured data)
                </Typography>
              </Box>
            </>
          )}

          {/* Comparison History Section */}
          {comparisonHistory.length > 0 && (
            <Box id="comparison-history" sx={{ mt: 4 }}>
              <Divider sx={{ mb: 3 }} />
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                <HistoryIcon color="primary" />
                <Typography variant="h5" fontWeight={700}>
                  📜 Comparison History
                </Typography>
                <Chip 
                  label={`${comparisonHistory.length} comparison${comparisonHistory.length !== 1 ? 's' : ''}`} 
                  size="small" 
                  color="primary" 
                />
                <Box sx={{ flex: 1 }} />
                <Button
                  variant="outlined"
                  size="small"
                  color="warning"
                  onClick={handleRemoveDuplicates}
                  sx={{ textTransform: 'none' }}
                >
                  🧹 Remove Duplicates
                </Button>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Previous comparisons for this document (most recent first)
              </Typography>

              {comparisonHistory.map((item, index) => (
                <Card key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, flex: 1, minWidth: '200px' }}>
                        {index + 1}. {item.query}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(item.timestamp).toLocaleString()}
                        </Typography>
                        <Button
                          variant="outlined"
                          size="small"
                          color="primary"
                          startIcon={<Refresh />}
                          onClick={() => handleRunAgain(item.query)}
                          disabled={loading}
                          sx={{ 
                            textTransform: 'none',
                            ml: 1
                          }}
                        >
                          Run Again
                        </Button>
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      {/* Conventional RAG Result */}
                      <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: '250px' }}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: '#fef5f8', border: '1px solid #f48fb1' }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: '#c2185b' }}>
                            📚 Conventional RAG
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block', mb: 1, opacity: 0.7 }}>
                            ⏱️ {item.conventional.time.toFixed(2)}s
                          </Typography>
                          <Typography variant="body2" sx={{ 
                            whiteSpace: 'pre-wrap', 
                            maxHeight: '300px', 
                            overflow: 'auto',
                            fontSize: '0.875rem',
                            lineHeight: 1.6,
                            pr: 1,
                            '&::-webkit-scrollbar': {
                              width: '8px',
                            },
                            '&::-webkit-scrollbar-track': {
                              bgcolor: 'rgba(0,0,0,0.05)',
                              borderRadius: '4px',
                            },
                            '&::-webkit-scrollbar-thumb': {
                              bgcolor: 'rgba(0,0,0,0.2)',
                              borderRadius: '4px',
                              '&:hover': {
                                bgcolor: 'rgba(0,0,0,0.3)',
                              },
                            },
                          }}>
                            {item.conventional.answer}
                          </Typography>
                        </Paper>
                      </Box>

                      {/* Hybrid RAG Result */}
                      <Box sx={{ flex: '1 1 calc(50% - 8px)', minWidth: '250px' }}>
                        <Paper elevation={0} sx={{ p: 2, bgcolor: '#e3f2fd', border: '1px solid #4facfe' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0288d1' }}>
                              🧠 Hybrid RAG
                            </Typography>
                            <Chip 
                              label={item.hybrid.route} 
                              size="small" 
                              sx={{ 
                                bgcolor: item.hybrid.route === 'table' ? '#fff3e0' : 
                                         item.hybrid.route === 'rag' ? '#f3e5f5' : '#e8f5e9',
                                fontSize: '0.7rem',
                                height: '20px'
                              }} 
                            />
                          </Box>
                          <Typography variant="caption" sx={{ display: 'block', mb: 1, opacity: 0.7 }}>
                            ⏱️ {item.hybrid.time.toFixed(2)}s
                          </Typography>
                          <Typography variant="body2" sx={{ 
                            whiteSpace: 'pre-wrap', 
                            maxHeight: '300px', 
                            overflow: 'auto',
                            fontSize: '0.875rem',
                            lineHeight: 1.6,
                            pr: 1,
                            '&::-webkit-scrollbar': {
                              width: '8px',
                            },
                            '&::-webkit-scrollbar-track': {
                              bgcolor: 'rgba(0,0,0,0.05)',
                              borderRadius: '4px',
                            },
                            '&::-webkit-scrollbar-thumb': {
                              bgcolor: 'rgba(0,0,0,0.3)',
                              borderRadius: '4px',
                              '&:hover': {
                                bgcolor: 'rgba(0,0,0,0.4)',
                              },
                            },
                          }}>
                            {item.hybrid.answer}
                          </Typography>
                        </Paper>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Container>
      </Box>

      {/* Cleanup Success/Error Snackbar */}
      <Snackbar
        open={!!cleanupMessage}
        autoHideDuration={4000}
        onClose={() => setCleanupMessage(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setCleanupMessage(null)} 
          severity={cleanupMessage?.includes('⚠️') ? 'warning' : 'success'}
          sx={{ width: '100%' }}
        >
          {cleanupMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ComparisonDemo;

