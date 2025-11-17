import React from 'react';
import { AuthProvider, RouterProvider, WebSocketProvider, ToastProvider, queryClient } from './Backend.jsx';
import Root from './Design.jsx';
import './Faircruit.css';

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider>
          <WebSocketProvider>
            <ToastProvider>
              <Root />
            </ToastProvider>
          </WebSocketProvider>
        </RouterProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;