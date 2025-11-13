// src/App.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  QueryClientProvider,
  queryClient,
  ToastProvider,
  RouterProvider,
  AuthProvider,
  WebSocketProvider,  // FIXED: Was WSProvider
  AppContent,
} from './faircruit.jsx';
import './Faircruit.css';

// === FULL APP WITH ALL PROVIDERS ===
const App = () => (
  <QueryClientProvider client={queryClient}>
    <ToastProvider>
      <RouterProvider>
        <AuthProvider>
          <WebSocketProvider>  {/* FIXED: Use WebSocketProvider */}
            <AppContent />
          </WebSocketProvider>
        </AuthProvider>
      </RouterProvider>
    </ToastProvider>
  </QueryClientProvider>
);

// === RENDER HERE ===
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);