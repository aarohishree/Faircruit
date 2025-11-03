// src/App.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  QueryClientProvider,
  queryClient,
  ToastProvider,
  RouterProvider,
  AuthProvider,
  WSProvider,
  AppContent,
} from './faircruit.jsx';
import './Faircruit.css';

// === FULL APP WITH ALL PROVIDERS ===
const App = () => (
  <QueryClientProvider client={queryClient}>
    <ToastProvider>
      <RouterProvider>
        <AuthProvider>
          <WSProvider>
            <AppContent />
          </WSProvider>
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