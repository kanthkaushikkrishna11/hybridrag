// Simple Sidebar component
import React from 'react';
import {
  Drawer,
  Box,
  Typography,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import FileUploader from '../Upload/FileUploader';
import type { PDFDocument } from '../../types';

const DRAWER_WIDTH = 360;

interface SidebarProps {
  currentDocument: PDFDocument | null;
  onUploadSuccess: (document: PDFDocument) => void;
  onUploadError: (error: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentDocument,
  onUploadSuccess,
  onUploadError,
}) => {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ p: 3, overflow: 'auto', height: '100vh' }}>
        <FileUploader
          currentDocument={currentDocument}
          onUploadSuccess={onUploadSuccess}
          onUploadError={onUploadError}
        />

        <Divider sx={{ my: 3 }} />

        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight={600}>
              📘 Quick Guide
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" paragraph>
              <strong>Getting Started:</strong>
            </Typography>
            <Box component="ol" sx={{ pl: 2, m: 0 }}>
              <li>
                <Typography variant="body2" color="text.secondary">
                  📤 Upload a PDF document
                </Typography>
              </li>
              <li>
                <Typography variant="body2" color="text.secondary">
                  ⏳ Wait for processing
                </Typography>
              </li>
              <li>
                <Typography variant="body2" color="text.secondary">
                  💬 Ask your questions
                </Typography>
              </li>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              <strong>Best Results:</strong>
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip label="Documents with tables" size="small" sx={{ m: 0.5 }} />
              <Chip label="Clear text formatting" size="small" sx={{ m: 0.5 }} />
              <Chip label="Searchable PDFs" size="small" sx={{ m: 0.5 }} />
            </Box>
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1" fontWeight={600}>
              🎯 System Capabilities
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                <Typography sx={{ mr: 1 }}>✨</Typography>
                <Typography variant="body2" color="text.secondary">
                  Text extraction & understanding
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                <Typography sx={{ mr: 1 }}>✨</Typography>
                <Typography variant="body2" color="text.secondary">
                  Table data processing with SQL
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                <Typography sx={{ mr: 1 }}>✨</Typography>
                <Typography variant="body2" color="text.secondary">
                  Semantic search with embeddings
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                <Typography sx={{ mr: 1 }}>✨</Typography>
                <Typography variant="body2" color="text.secondary">
                  Intelligent query routing (LangGraph)
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Typography sx={{ mr: 1 }}>✨</Typography>
                <Typography variant="body2" color="text.secondary">
                  Context-aware responses
                </Typography>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            Powered by
          </Typography>
          <Typography variant="body2" color="text.secondary">
            🧠 LangGraph
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ⚡ Gemini AI • Pinecone • PostgreSQL
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
