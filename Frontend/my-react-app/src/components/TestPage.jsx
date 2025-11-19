import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../Backend.jsx';
import CodeEditor from './CodeEditor.jsx';

const TestPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { isLoggedIn, user } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [testStarted, setTestStarted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [cheatingDetected, setCheatingDetected] = useState(false);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const videoRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/get-started');
    }
  }, [isLoggedIn, navigate]);

  // Fetch questions
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await fetch(`/api/v1/generate-questions/${jobId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        const data = await response.json();
        setQuestions(data.questions || getMockQuestions());
        setTimeRemaining(data.duration_minutes * 60 || 3600); // Default 60 min
      } catch (error) {
        console.error('Error fetching questions:', error);
        setQuestions(getMockQuestions());
        setTimeRemaining(3600);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [jobId]);

  // Timer
  useEffect(() => {
    if (!testStarted || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          submitTest();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [testStarted, timeRemaining]);

  // Anti-cheat: Detect tab switches
  useEffect(() => {
    if (!testStarted) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabSwitchCount(prev => prev + 1);
        if (prev >= 2) {
          setCheatingDetected(true);
        }
      }
    };

    const handleWindowBlur = () => {
      setTabSwitchCount(prev => prev + 1);
      if (prev >= 2) {
        setCheatingDetected(true);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
    };
  }, [testStarted, tabSwitchCount]);

  // Initialize webcam
  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        mediaStreamRef.current = stream;
      }
    } catch (error) {
      console.error('Error accessing webcam:', error);
    }
  }, []);

  const stopWebcam = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  const startTest = () => {
    startWebcam();
    setTestStarted(true);
  };

  const handleAnswerChange = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const submitTest = async () => {
    try {
      stopWebcam();
      
      const response = await fetch(`/api/v1/submit-test/${jobId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          answers,
          cheating_detected: cheatingDetected,
          tab_switches: tabSwitchCount
        })
      });

      const result = await response.json();
      navigate(`/results/${result.test_id}`);
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Error submitting test. Please try again.');
    }
  };

  if (loading) {
    return <div className="test-loading">Loading test...</div>;
  }

  if (cheatingDetected) {
    return (
      <div className="cheating-alert">
        <h2>⚠️ Test Suspended</h2>
        <p>Suspicious activity detected. This test has been suspended.</p>
        <button onClick={() => navigate('/')}>Return Home</button>
      </div>
    );
  }

  if (!testStarted) {
    return (
      <div className="test-start-screen">
        <div className="start-content">
          <h1>Test Instructions</h1>
          <div className="instructions">
            <h3>Before You Start:</h3>
            <ul>
              <li>✓ Find a quiet, well-lit environment</li>
              <li>✓ Ensure your webcam is working (for proctoring)</li>
              <li>✓ Close all unnecessary tabs and applications</li>
              <li>✓ Have a pen and paper if needed</li>
              <li>✓ This test is timed - you cannot pause it</li>
            </ul>

            <h3>Question Types:</h3>
            <ul>
              <li>📝 <strong>MCQ</strong> - Select one correct answer</li>
              <li>✍️ <strong>Short Answer</strong> - Type your response (3-5 sentences)</li>
              <li>📄 <strong>Essay</strong> - Detailed answer (5-10 minutes)</li>
              <li>💻 <strong>Code Review</strong> - Find bugs and suggest fixes</li>
            </ul>

            <h3>Anti-Cheat Policy:</h3>
            <ul>
              <li>⚠️ Switching tabs will be recorded</li>
              <li>⚠️ More than 3 tab switches will suspend your test</li>
              <li>⚠️ Your webcam is recording for proctoring</li>
            </ul>
          </div>

          <button className="btn btn-primary start-btn" onClick={startTest}>
            I Understand & Start Test
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div className="test-page">
      <div className="test-header">
        <div className="test-progress">
          <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        <div className="test-info">
          <div className="timer" style={{ color: timeRemaining < 300 ? '#e53e3e' : '#2d3748' }}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
          <div className="cheating-status">
            Tab Switches: {tabSwitchCount}/3
          </div>
        </div>
      </div>

      <div className="test-container">
        <div className="test-content">
          <div className="question-section">
            <h2 className={`question-type ${currentQuestion.type}`}>
              {getQuestionTypeLabel(currentQuestion.type)}
            </h2>
            <p className="question-text">{currentQuestion.question}</p>

            <div className="question-input">
              {currentQuestion.type === 'mcq' && (
                <div className="mcq-options">
                  {currentQuestion.options.map((option, idx) => (
                    <label key={idx} className="option">
                      <input
                        type="radio"
                        name={`q-${currentQuestionIndex}`}
                        value={idx}
                        checked={answers[currentQuestionIndex] === idx}
                        onChange={() => handleAnswerChange(currentQuestionIndex, idx)}
                      />
                      <span>{option}</span>
                    </label>
                  ))}
                </div>
              )}

              {currentQuestion.type === 'short_answer' && (
                <textarea
                  placeholder="Type your answer (2-3 sentences)..."
                  value={answers[currentQuestionIndex] || ''}
                  onChange={(e) => handleAnswerChange(currentQuestionIndex, e.target.value)}
                  className="answer-textarea"
                  rows="4"
                />
              )}

              {currentQuestion.type === 'essay' && (
                <textarea
                  placeholder="Type your detailed answer (5-10 minutes of content)..."
                  value={answers[currentQuestionIndex] || ''}
                  onChange={(e) => handleAnswerChange(currentQuestionIndex, e.target.value)}
                  className="answer-textarea"
                  rows="8"
                />
              )}

              {currentQuestion.type === 'code_debug' && (
                <CodeEditor
                  initialCode={currentQuestion.initial_code}
                  onChange={(code) => handleAnswerChange(currentQuestionIndex, code)}
                  value={answers[currentQuestionIndex] || currentQuestion.initial_code}
                />
              )}

              {currentQuestion.type === 'code_review' && (
                <div className="code-review">
                  <div className="code-section">
                    <h4>Code to Review:</h4>
                    <pre><code>{currentQuestion.initial_code}</code></pre>
                  </div>
                  <textarea
                    placeholder="Identify bugs, explain issues, and suggest fixes..."
                    value={answers[currentQuestionIndex] || ''}
                    onChange={(e) => handleAnswerChange(currentQuestionIndex, e.target.value)}
                    className="answer-textarea"
                    rows="6"
                  />
                </div>
              )}
            </div>

            <div className="time-hint">
              ⏱️ Suggested time: {currentQuestion.time_limit_seconds / 60} minutes
            </div>
          </div>
        </div>

        <div className="test-sidebar">
          <div className="webcam-section">
            <h4>Proctoring</h4>
            <video
              ref={videoRef}
              autoPlay
              muted
              className="webcam-feed"
            />
          </div>

          <div className="navigation">
            <button
              className="btn btn-sm"
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0}
            >
              ← Previous
            </button>

            <button
              className="btn btn-sm"
              onClick={() => setCurrentQuestionIndex(Math.min(questions.length - 1, currentQuestionIndex + 1))}
              disabled={currentQuestionIndex === questions.length - 1}
            >
              Next →
            </button>
          </div>

          <button
            className="btn btn-primary btn-submit"
            onClick={submitTest}
          >
            Submit Test
          </button>
        </div>
      </div>

      <style>{`
        .test-page {
          min-height: 100vh;
          background: #f5f7fa;
        }

        .test-header {
          background: white;
          padding: 20px;
          border-bottom: 2px solid #e2e8f0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .test-progress {
          flex: 1;
        }

        .progress-bar {
          width: 300px;
          height: 8px;
          background: #e2e8f0;
          border-radius: 4px;
          overflow: hidden;
          margin-top: 8px;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea, #764ba2);
          transition: width 0.3s;
        }

        .test-info {
          display: flex;
          gap: 30px;
          align-items: center;
        }

        .timer {
          font-size: 1.2rem;
          font-weight: 700;
          font-family: 'Courier New', monospace;
        }

        .cheating-status {
          font-size: 0.9rem;
          color: #718096;
        }

        .test-container {
          display: grid;
          grid-template-columns: 1fr 350px;
          gap: 24px;
          padding: 24px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .test-content {
          background: white;
          border-radius: 12px;
          padding: 32px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .question-type {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 600;
          margin-bottom: 16px;
        }

        .question-type.mcq {
          background: #bee3f8;
          color: #2c5aa0;
        }

        .question-type.short_answer {
          background: #c6f6d5;
          color: #22543d;
        }

        .question-type.essay {
          background: #feebc8;
          color: #7c2d12;
        }

        .question-type.code_debug {
          background: #e9d8fd;
          color: #44337a;
        }

        .question-text {
          font-size: 1.2rem;
          color: #2d3748;
          margin-bottom: 24px;
          line-height: 1.8;
        }

        .question-input {
          margin-bottom: 24px;
        }

        .mcq-options {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .option {
          display: flex;
          align-items: center;
          padding: 12px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .option:hover {
          border-color: #667eea;
          background: #f7fafc;
        }

        .option input[type="radio"] {
          margin-right: 12px;
          cursor: pointer;
        }

        .answer-textarea {
          width: 100%;
          padding: 12px;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          font-family: 'Segoe UI', sans-serif;
          font-size: 1rem;
          resize: vertical;
        }

        .answer-textarea:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .code-review {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .code-section {
          background: #2d3748;
          border-radius: 8px;
          padding: 16px;
          overflow-x: auto;
        }

        .code-section h4 {
          color: #e2e8f0;
          margin: 0 0 12px 0;
        }

        .code-section pre {
          margin: 0;
          color: #e2e8f0;
          font-family: 'Courier New', monospace;
          font-size: 0.9rem;
        }

        .time-hint {
          color: #718096;
          font-size: 0.9rem;
          margin-top: 16px;
        }

        .test-sidebar {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .webcam-section {
          background: white;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .webcam-section h4 {
          margin: 0 0 12px 0;
        }

        .webcam-feed {
          width: 100%;
          border-radius: 8px;
          background: #2d3748;
        }

        .navigation {
          display: flex;
          gap: 8px;
        }

        .btn-sm {
          flex: 1;
          padding: 10px;
          font-size: 0.9rem;
        }

        .btn-submit {
          width: 100%;
          padding: 12px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .test-loading,
        .cheating-alert {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: #f5f7fa;
          font-size: 1.2rem;
        }

        .cheating-alert {
          flex-direction: column;
          gap: 20px;
        }

        .test-start-screen {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .start-content {
          background: white;
          border-radius: 12px;
          padding: 40px;
          max-width: 700px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .instructions {
          margin: 24px 0;
        }

        .instructions h3 {
          color: #667eea;
          margin-top: 20px;
          margin-bottom: 12px;
        }

        .instructions ul {
          list-style: none;
          padding: 0;
        }

        .instructions li {
          padding: 8px 0;
          color: #2d3748;
          line-height: 1.6;
        }

        .start-btn {
          width: 100%;
          padding: 14px;
          margin-top: 20px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
        }

        @media (max-width: 1024px) {
          .test-container {
            grid-template-columns: 1fr;
          }

          .test-sidebar {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
          }
        }

        @media (max-width: 768px) {
          .test-header {
            flex-direction: column;
            gap: 16px;
          }

          .test-sidebar {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`;
}

function getQuestionTypeLabel(type) {
  const labels = {
    'mcq': '📋 Multiple Choice',
    'short_answer': '✍️ Short Answer',
    'essay': '📄 Essay',
    'code_debug': '💻 Code Review',
    'code_review': '💻 Code Review'
  };
  return labels[type] || type;
}

function getMockQuestions() {
  return [
    {
      type: 'mcq',
      question: 'What is the time complexity of binary search?',
      options: ['O(n)', 'O(log n)', 'O(n²)', 'O(2ⁿ)'],
      time_limit_seconds: 120
    },
    {
      type: 'short_answer',
      question: 'Explain the difference between Git merge and Git rebase.',
      time_limit_seconds: 600
    },
    {
      type: 'essay',
      question: 'Design a scalable system architecture for a social media platform. Consider load balancing, database design, and caching strategies.',
      time_limit_seconds: 900
    },
    {
      type: 'code_debug',
      question: 'Fix the following code that should calculate factorial but has a bug:',
      initial_code: `def factorial(n):
  if n == 0:
    return 1
  return n * factorial(n)  # Bug here!`,
      time_limit_seconds: 1200
    }
  ];
}

export default TestPage;
