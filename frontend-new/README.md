# Hybrid RAG Frontend

Modern React + TypeScript frontend for the Hybrid RAG system.

## 🚀 Features

- **React 18** with **TypeScript** for type safety
- **Material-UI (MUI)** for beautiful, consistent UI components
- **Proper Chat Flow** - User messages appear immediately, no more waiting
- **Smart Response Formatting** - Raw table data converted to readable bullet points
- **Real-time Upload Progress** - Visual feedback during PDF processing
- **Error Handling** - Clear, user-friendly error messages
- **Responsive Design** - Works on desktop and mobile

## 📋 Prerequisites

- Node.js 16+ and npm
- Backend running on `http://localhost:8010`

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Create .env file (if not exists)
echo "VITE_API_URL=http://localhost:8010" > .env

# Start development server
npm run dev
```

The app will open at **http://localhost:7000**

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── Chat/           # Chat-related components
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   └── ChatWindow.tsx
│   ├── Upload/         # File upload
│   │   └── FileUploader.tsx
│   └── Layout/         # Layout components
│       └── Sidebar.tsx
├── services/           # API services
│   └── api.ts         # Backend communication
├── types/             # TypeScript types
│   └── index.ts
├── hooks/             # Custom React hooks
│   └── useChat.ts
├── utils/             # Utility functions
│   └── formatResponse.ts
├── App.tsx            # Main app component
└── main.tsx           # Entry point
```

## 🎨 Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI v5** - Component library
- **Vite** - Fast build tool
- **Axios** - HTTP client

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:8010
```

### Port Configuration

The frontend runs on port **7000** by default. To change:

Edit `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 7000, // Change this
  },
});
```

## 🚀 Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run tsc

# Lint
npm run lint
```

## ✨ Key Features Explained

### Proper Chat Flow
Unlike the Streamlit version, messages appear instantly:
1. User types and sends message
2. **User message displays immediately** ✅
3. Loading indicator shows below
4. Assistant response appears when ready

### Smart Response Formatting
Raw API responses like:
```
Uruguay | 1930 Italy | 1934 Italy | 1938
```

Are formatted to:
```
• Uruguay (1930)
• Italy (1934)
• Italy (1938)
```

### Material-UI Theme
Custom theme with:
- Primary: Purple gradient (#667eea)
- Secondary: Deep purple (#764ba2)
- Clean, modern design
- Consistent spacing and typography

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 7000
lsof -ti:7000 | xargs kill -9
```

### Backend connection issues
1. Ensure backend is running on port 8010
2. Check `.env` file has correct `VITE_API_URL`
3. Check browser console for CORS errors

### Build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Material-UI Documentation](https://mui.com/)
- [Vite Documentation](https://vitejs.dev/)

## 🤝 Contributing

This is a complete rewrite of the Streamlit frontend to address:
- ❌ Streamlit's limited chat UX
- ❌ Inability to show user messages immediately
- ❌ Poor response formatting
- ✅ Now with proper React + TypeScript
- ✅ Better error handling
- ✅ Professional UI/UX

## 📄 License

Same as parent project.
