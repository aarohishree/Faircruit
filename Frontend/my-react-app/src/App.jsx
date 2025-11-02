import React from 'react';
import ReactDOM from 'react-dom/client';
import './Faircruit.css';
import Faircruit from './Faircruit.jsx';



ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <ToastProvider>
                <AuthProvider>
                    <WebSocketProvider>
                        <Faircruit />
                    </WebSocketProvider>
                </AuthProvider>
            </ToastProvider>
        </QueryClientProvider>
    </React.StrictMode>
);