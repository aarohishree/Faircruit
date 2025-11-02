import { useState, useEffect } from 'react';
import { useAuth } from './auth-context';
import { authAxios } from './api';

export const useMLService = () => {
    const [mlStatus, setMLStatus] = useState('connecting');
    const { token } = useAuth();
    
    // ML Service status check
    useEffect(() => {
        const checkMLStatus = async () => {
            try {
                const response = await authAxios.get('/api/ml/status');
                setMLStatus(response.data.status);
            } catch (error) {
                setMLStatus('error');
                console.error('ML service error:', error);
            }
        };
        
        if (token) {
            checkMLStatus();
            const interval = setInterval(checkMLStatus, 30000); // Check every 30s
            return () => clearInterval(interval);
        }
    }, [token]);

    const analyzeCV = async (cvText) => {
        try {
            const response = await authAxios.post('/api/ml/analyze-cv', { cv_text: cvText });
            return response.data;
        } catch (error) {
            console.error('CV analysis error:', error);
            throw error;
        }
    };

    const evaluateSubmission = async (submissionData) => {
        try {
            const response = await authAxios.post('/api/ml/evaluate-submission', submissionData);
            return response.data;
        } catch (error) {
            console.error('Submission evaluation error:', error);
            throw error;
        }
    };

    const generateQuestions = async (level, role) => {
        try {
            const response = await authAxios.post('/api/ml/generate-questions', { level, role });
            return response.data;
        } catch (error) {
            console.error('Question generation error:', error);
            throw error;
        }
    };

    return {
        mlStatus,
        analyzeCV,
        evaluateSubmission,
        generateQuestions,
    };
};