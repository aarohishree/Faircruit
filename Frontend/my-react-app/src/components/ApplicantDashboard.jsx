import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../Backend.jsx';

/**
 * ApplicantDashboard - Main hub for applicants
 * - Browse available jobs
 * - Take Gemini-generated tests
 * - View results and analysis
 */
const ApplicantDashboard = () => {
  const { isLoggedIn, user, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('jobs'); // jobs, test, results
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [testInProgress, setTestInProgress] = useState(false);
  const [testSubmitted, setTestSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [cheatingDetected, setCheatingDetected] = useState(false);
  const videoRef = useRef(null);
  const mediaStreamRef = useRef(null);
  
  // Error & Status Handling
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isLoadingTest, setIsLoadingTest] = useState(false);
  const [isSubmittingTest, setIsSubmittingTest] = useState(false);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsPollCount, setResultsPollCount] = useState(0);

  // Redirect if not logged in
  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login');
      return;
    }
  }, [isLoggedIn, navigate]);

  // Fetch available jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('/api/v1/jobs', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });
        const data = await response.json();
        setJobs(data.items || data.jobs || getMockJobs());
      } catch (error) {
        console.error('Error fetching jobs:', error);
        setJobs(getMockJobs());
      } finally {
        setLoading(false);
      }
    };

    if (tab === 'jobs') {
      fetchJobs();
    }
  }, [tab]);

  // Timer logic
  useEffect(() => {
    if (!testInProgress || timeRemaining <= 0 || testSubmitted) return;

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
  }, [testInProgress, timeRemaining, testSubmitted]);

  // Anti-cheat: Tab switch detection
  useEffect(() => {
    if (!testInProgress) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabSwitchCount(prev => prev + 1);
        if (prev >= 2) {
          setCheatingDetected(true);
          alert('⚠️ Test suspended due to suspicious activity!');
          submitTest();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [testInProgress, tabSwitchCount]);

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

  // Start test for selected job
  const startTest = async (jobId) => {
    try {
      setError(null);
      setSuccess(null);
      setIsLoadingTest(true);
      setStatusMessage('Initializing test...');
      
      const token = localStorage.getItem('authToken');
      console.log('Token present:', !!token, 'Token:', token?.substring(0, 20) + '...');
      const job = jobs.find(j => j._id === jobId || j.id === jobId);
      setSelectedJob(job);

      // Step 1: Create an application for this job
      setStatusMessage('Creating application...');
      const requestBody = { job_id: jobId };
      console.log('Sending apply request with body:', requestBody);
      const appResponse = await fetch(`/api/v1/applicant/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!appResponse.ok) {
        let errData;
        try {
          errData = await appResponse.json();
        } catch (e) {
          errData = { error: appResponse.statusText };
        }
        console.error('Apply endpoint error status:', appResponse.status);
        console.error('Apply endpoint error data:', errData);
        const errorMsg = errData.detail || (Array.isArray(errData) && errData[0]?.msg) || JSON.stringify(errData);
        throw new Error(`Application creation failed (${appResponse.status}): ${errorMsg}`);
      }

      const appData = await appResponse.json();
      const applicationId = appData._id || appData.id;
      setSuccess('✓ Application created');
      setStatusMessage('Generating test questions...');
      
      // Store application ID for later submission
      setSelectedJob(prev => ({ ...prev, applicationId }));

      // Step 2: Generate test questions
      const qResponse = await fetch(`/api/v1/applicant/generate-questions/${jobId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!qResponse.ok) {
        const errData = await qResponse.json();
        throw new Error(`Question generation failed: ${errData.detail || qResponse.statusText}`);
      }

      const qData = await qResponse.json();
      setSuccess('✓ Test questions generated');
      
      // Convert questions dict to array (backend returns {level_1, level_2, ...})
      const questionsDict = qData.questions;
      const questionsArray = [];
      
      if (typeof questionsDict === 'object' && !Array.isArray(questionsDict)) {
        for (let i = 1; i <= 4; i++) {
          const levelKey = `level_${i}`;
          if (questionsDict[levelKey]) {
            questionsArray.push({
              level: i,
              ...questionsDict[levelKey]
            });
          }
        }
      } else if (Array.isArray(questionsDict)) {
        questionsArray.push(...questionsDict);
      }

      const totalTime = questionsArray.reduce((sum, q) => sum + (q.time_limit_seconds || 600), 0);
      
      setQuestions(questionsArray.length > 0 ? questionsArray : getMockQuestions());
      setTimeRemaining(totalTime || 3600);
      setCurrentQuestionIndex(0);
      setAnswers({});
      setTabSwitchCount(0);
      setCheatingDetected(false);
      setTestInProgress(true);
      setTestSubmitted(false);
      setStatusMessage(null);
      
      startWebcam();
      setTab('test');
    } catch (error) {
      console.error('Error starting test:', error);
      setError('❌ ' + error.message);
      setIsLoadingTest(false);
    } finally {
      setIsLoadingTest(false);
    }
  };

  // Handle answer changes
  const handleAnswerChange = (value) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestionIndex]: value
    }));
  };

  // Navigate between questions
  const goNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const goPrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  // Submit test
  const submitTest = async () => {
    try {
      setError(null);
      setSuccess(null);
      setIsSubmittingTest(true);
      setStatusMessage('Submitting test...');
      stopWebcam();

      if (!selectedJob?.applicationId) {
        throw new Error('Application ID not found. Please start the test again.');
      }

      // Format answers according to backend schema
      const testAnswers = {};
      questions.forEach((q, idx) => {
        testAnswers[idx] = answers[idx] || '';
      });

      const response = await fetch(`/api/v1/applicant/tests/${selectedJob.applicationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          answers: testAnswers
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(`Test submission failed: ${errData.detail || response.statusText}`);
      }

      const result = await response.json();
      setSuccess('✓ Test submitted successfully');
      setStatusMessage('Gemini AI is analyzing your responses...');
      
      setTestInProgress(false);
      setTestSubmitted(true);
      setResults(null);
      setResultsPollCount(0);
      
      setTab('results');
      
      // Auto-poll for results every 3 seconds for up to 30 attempts (90 seconds)
      pollForResults(selectedJob.applicationId);
    } catch (error) {
      console.error('Error submitting test:', error);
      setError('❌ ' + error.message);
      setIsSubmittingTest(false);
    }
  };

  // Poll for results with auto-retry
  const pollForResults = async (applicationId, attempt = 0) => {
    if (attempt > 30) {
      setStatusMessage('Results generation taking longer than expected. Please refresh in a few moments.');
      return;
    }

    try {
      setResultsLoading(true);
      const response = await fetch(`/api/v1/applicant/results/${applicationId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
      });

      if (response.ok) {
        const result = await response.json();
        setResults(result);
        setSuccess('✓ Results ready!');
        setStatusMessage(null);
        setResultsLoading(false);
        setIsSubmittingTest(false);
      } else if (response.status === 400) {
        // Results not ready yet, poll again
        setResultsPollCount(attempt + 1);
        setStatusMessage(`Gemini analyzing... (${attempt + 1}/30)`);
        setTimeout(() => pollForResults(applicationId, attempt + 1), 3000);
      } else {
        throw new Error(`Failed to fetch results: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching results:', error);
      if (attempt < 30) {
        setTimeout(() => pollForResults(applicationId, attempt + 1), 3000);
      } else {
        setError('❌ Could not retrieve results after multiple attempts');
        setResultsLoading(false);
        setIsSubmittingTest(false);
      }
    }
  };

  if (!isLoggedIn) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Redirecting...</div>;
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;

  return (
    <div className="applicant-dashboard" style={styles.dashboard}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h2 style={{ margin: 0 }}>Faircruit Applicant Dashboard</h2>
          <div style={styles.userInfo}>
            <span>Welcome, <strong>{user?.username}</strong></span>
            <button onClick={logout} style={styles.btnSmall}>Logout</button>
          </div>
        </div>
      </header>

      {/* Message Alerts */}
      {error && (
        <div style={styles.alertError}>
          <div style={styles.alertContent}>
            {error}
            <button 
              onClick={() => setError(null)} 
              style={styles.alertClose}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {success && (
        <div style={styles.alertSuccess}>
          <div style={styles.alertContent}>
            {success}
            <button 
              onClick={() => setSuccess(null)} 
              style={styles.alertClose}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {statusMessage && (
        <div style={styles.alertStatus}>
          <div style={styles.alertContent}>
            {statusMessage}
          </div>
        </div>
      )}

      <div style={styles.container}>
        {/* Tab Navigation */}
        <div style={styles.tabs}>
          <button
            style={{ ...styles.tab, ...(tab === 'jobs' ? styles.tabActive : {}) }}
            onClick={() => setTab('jobs')}
          >
            📋 Available Jobs
          </button>
          <button
            style={{ ...styles.tab, ...(tab === 'test' ? styles.tabActive : {}) }}
            onClick={() => setTab('test')}
            disabled={!testInProgress}
          >
            📝 Test ({currentQuestionIndex + 1}/{questions.length})
          </button>
          <button
            style={{ ...styles.tab, ...(tab === 'results' ? styles.tabActive : {}) }}
            onClick={() => setTab('results')}
            disabled={!testSubmitted}
          >
            ✓ Results
          </button>
        </div>

        {/* JOBS TAB */}
        {tab === 'jobs' && (
          <div style={styles.content}>
            <h3>Available Job Positions</h3>
            {loading ? (
              <p>Loading jobs...</p>
            ) : jobs.length === 0 ? (
              <p>No jobs available at the moment.</p>
            ) : (
              <div style={styles.jobsGrid}>
                {jobs.map(job => (
                  <div key={job.id} style={styles.jobCard}>
                    <h4>{job.title}</h4>
                    <p style={styles.roleLabel}>{job.role || 'General'}</p>
                    <p style={styles.description}>{job.description?.substring(0, 150)}...</p>
                    <div style={styles.jobMeta}>
                      <span>⏱️ {job.duration_minutes || 60} min</span>
                      <span>❓ {job.num_questions || 4} questions</span>
                    </div>
                    <button
                      style={styles.btnPrimary}
                      onClick={() => startTest(job._id || job.id)}
                    >
                      Start Test
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TEST TAB */}
        {tab === 'test' && testInProgress && currentQuestion && (
          <div style={styles.content}>
            {/* Test Header */}
            <div style={styles.testHeader}>
              <div>
                <p>Question {currentQuestionIndex + 1} of {questions.length}</p>
                <div style={styles.progressBar}>
                  <div style={{ ...styles.progressFill, width: `${progress}%` }}></div>
                </div>
              </div>
              <div style={styles.testInfo}>
                <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: timeRemaining < 300 ? '#e53e3e' : '#2d3748' }}>
                  ⏱️ {formatTime(timeRemaining)}
                </span>
                <span>🔴 Tab Switches: {tabSwitchCount}/3</span>
              </div>
            </div>

            {/* Question */}
            <div style={styles.questionBox}>
              <div style={styles.questionType}>
                {getQuestionTypeLabel(currentQuestion.type)}
              </div>
              <h3 style={styles.questionText}>{currentQuestion.question}</h3>

              {/* Answer Input */}
              <div style={styles.answerInput}>
                {currentQuestion.type === 'mcq' && (
                  <div>
                    {currentQuestion.options?.map((option, idx) => (
                      <label key={idx} style={styles.radioOption}>
                        <input
                          type="radio"
                          name="answer"
                          checked={answers[currentQuestionIndex] == idx}
                          onChange={() => handleAnswerChange(idx)}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                )}

                {(currentQuestion.type === 'short_answer' || currentQuestion.type === 'essay') && (
                  <textarea
                    placeholder={`Your answer (${currentQuestion.type === 'short_answer' ? '2-3' : '5-10'} minutes)...`}
                    value={answers[currentQuestionIndex] || ''}
                    onChange={e => handleAnswerChange(e.target.value)}
                    style={styles.textarea}
                    rows={currentQuestion.type === 'essay' ? 8 : 4}
                  />
                )}

                {(currentQuestion.type === 'code_debug' || currentQuestion.type === 'code_review') && (
                  <div>
                    <div style={styles.codeBlock}>
                      <pre><code>{currentQuestion.initial_code}</code></pre>
                    </div>
                    <textarea
                      placeholder="Your analysis and fixes..."
                      value={answers[currentQuestionIndex] || ''}
                      onChange={e => handleAnswerChange(e.target.value)}
                      style={styles.textarea}
                      rows={6}
                    />
                  </div>
                )}
              </div>

              <p style={styles.timeHint}>
                Suggested time: {currentQuestion.time_limit_seconds / 60} minutes
              </p>
            </div>

            {/* Navigation */}
            <div style={styles.testNavigation}>
              <button
                style={styles.btnSecondary}
                onClick={goPrevQuestion}
                disabled={currentQuestionIndex === 0}
              >
                ← Previous
              </button>
              <button
                style={styles.btnSecondary}
                onClick={goNextQuestion}
                disabled={currentQuestionIndex === questions.length - 1}
              >
                Next →
              </button>
              <button
                style={styles.btnSuccess}
                onClick={submitTest}
              >
                Submit Test
              </button>
            </div>

            {/* Webcam */}
            <div style={styles.webcamSection}>
              <h4>Proctoring Webcam</h4>
              <video
                ref={videoRef}
                autoPlay
                muted
                style={styles.webcam}
              />
            </div>
          </div>
        )}

        {/* RESULTS TAB */}
        {tab === 'results' && testSubmitted && (
          <div style={styles.content}>
            <h3>Test Results</h3>
            
            {results ? (
              <>
                <div style={styles.scoreSection}>
                  <div style={styles.scoreCard}>
                    <h2 style={styles.score}>
                      {results.score || results.overall_score || 'Pending'}
                    </h2>
                    <p>{results.status || 'Evaluating...'}</p>
                  </div>
                </div>

                {results.narrative && (
                  <div style={styles.feedback}>
                    <h4>Gemini Analysis</h4>
                    <p>{results.narrative}</p>
                  </div>
                )}

                {results.recommendations && (
                  <div style={styles.feedback}>
                    <h4>Recommendations</h4>
                    <p>{results.recommendations}</p>
                  </div>
                )}

                {results.profile?.score !== undefined && (
                  <div style={styles.stats}>
                    <h4>Detailed Score</h4>
                    <p>Score: {results.profile.score}/100</p>
                  </div>
                )}
              </>
            ) : (
              <div style={styles.scoreSection}>
                <p style={{ fontSize: '1.1rem', color: '#2d3748' }}>
                  ⏳ Your test has been submitted successfully!
                </p>
                <p>Gemini AI is currently analyzing your responses. This may take 30-60 seconds.</p>
                <p>Please refresh this page in a moment to see your results.</p>
                <button
                  style={{ ...styles.btnSecondary, marginTop: '20px' }}
                  onClick={() => fetchResults(selectedJob.applicationId)}
                >
                  🔄 Check Results
                </button>
              </div>
            )}

            <button
              style={styles.btnPrimary}
              onClick={() => {
                setTab('jobs');
                setTestSubmitted(false);
                setSelectedJob(null);
              }}
            >
              Back to Jobs
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ─── STYLES ──────────────────────────────────────────────────────────
const styles = {
  dashboard: {
    minHeight: '100vh',
    background: '#f5f7fa',
  },
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  userInfo: {
    display: 'flex',
    gap: '15px',
    alignItems: 'center',
  },
  btnSmall: {
    padding: '8px 16px',
    background: 'white',
    color: '#667eea',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '30px 20px',
  },
  tabs: {
    display: 'flex',
    gap: '10px',
    marginBottom: '30px',
    borderBottom: '2px solid #e2e8f0',
  },
  tab: {
    padding: '12px 24px',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: '600',
    color: '#718096',
    borderBottom: '3px solid transparent',
    transition: 'all 0.3s',
  },
  tabActive: {
    color: '#667eea',
    borderBottom: '3px solid #667eea',
  },
  content: {
    background: 'white',
    borderRadius: '12px',
    padding: '30px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  jobsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
    marginTop: '20px',
  },
  jobCard: {
    border: '2px solid #e2e8f0',
    borderRadius: '12px',
    padding: '20px',
    transition: 'all 0.3s',
  },
  roleLabel: {
    display: 'inline-block',
    background: '#667eea',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '0.85rem',
    margin: '10px 0',
  },
  description: {
    color: '#718096',
    lineHeight: '1.6',
    margin: '10px 0',
  },
  jobMeta: {
    display: 'flex',
    gap: '15px',
    margin: '15px 0',
    fontSize: '0.9rem',
    color: '#a0aec0',
  },
  btnPrimary: {
    width: '100%',
    padding: '12px',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
    marginTop: '10px',
  },
  testHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    padding: '20px',
    background: '#f7fafc',
    borderRadius: '8px',
  },
  progressBar: {
    width: '300px',
    height: '8px',
    background: '#e2e8f0',
    borderRadius: '4px',
    overflow: 'hidden',
    marginTop: '10px',
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #667eea, #764ba2)',
    transition: 'width 0.3s',
  },
  testInfo: {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
  },
  questionBox: {
    marginBottom: '30px',
  },
  questionType: {
    display: 'inline-block',
    background: '#bee3f8',
    color: '#2c5aa0',
    padding: '6px 12px',
    borderRadius: '6px',
    fontSize: '0.85rem',
    fontWeight: '600',
    marginBottom: '10px',
  },
  questionText: {
    fontSize: '1.2rem',
    marginBottom: '20px',
    lineHeight: '1.8',
  },
  answerInput: {
    marginBottom: '20px',
  },
  radioOption: {
    display: 'flex',
    alignItems: 'center',
    padding: '12px',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
    marginBottom: '10px',
    cursor: 'pointer',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
    fontFamily: 'monospace',
    fontSize: '1rem',
    resize: 'vertical',
  },
  codeBlock: {
    background: '#2d3748',
    color: '#e2e8f0',
    padding: '15px',
    borderRadius: '8px',
    overflow: 'auto',
    marginBottom: '15px',
  },
  timeHint: {
    color: '#718096',
    fontSize: '0.9rem',
    marginTop: '10px',
  },
  testNavigation: {
    display: 'flex',
    gap: '10px',
    marginTop: '20px',
  },
  btnSecondary: {
    flex: 1,
    padding: '12px',
    background: '#e2e8f0',
    color: '#2d3748',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  btnSuccess: {
    flex: 1,
    padding: '12px',
    background: '#48bb78',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  webcamSection: {
    marginTop: '30px',
    padding: '20px',
    background: '#f7fafc',
    borderRadius: '8px',
  },
  webcam: {
    width: '100%',
    maxWidth: '400px',
    borderRadius: '8px',
    background: '#2d3748',
  },
  scoreSection: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '30px',
  },
  scoreCard: {
    textAlign: 'center',
    padding: '30px',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    borderRadius: '12px',
    minWidth: '250px',
  },
  score: {
    fontSize: '3.5rem',
    margin: '10px 0',
  },
  feedback: {
    background: '#f7fafc',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    borderLeft: '4px solid #667eea',
  },
  stats: {
    background: '#f7fafc',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  alertError: {
    background: '#fee',
    border: '1px solid #fcc',
    borderLeft: '4px solid #e53e3e',
    padding: '12px 16px',
    margin: '10px 20px',
    borderRadius: '4px',
    animation: 'slideDown 0.3s ease-out'
  },
  alertSuccess: {
    background: '#efe',
    border: '1px solid #cfc',
    borderLeft: '4px solid #38a169',
    padding: '12px 16px',
    margin: '10px 20px',
    borderRadius: '4px',
    animation: 'slideDown 0.3s ease-out'
  },
  alertStatus: {
    background: '#eff6ff',
    border: '1px solid #bee3f8',
    borderLeft: '4px solid #3182ce',
    padding: '12px 16px',
    margin: '10px 20px',
    borderRadius: '4px',
    animation: 'slideDown 0.3s ease-out'
  },
  alertContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '0.95rem',
    color: '#2d3748'
  },
  alertClose: {
    background: 'none',
    border: 'none',
    color: '#718096',
    cursor: 'pointer',
    fontSize: '1.2rem',
    padding: '0 0 0 16px',
    marginLeft: 'auto'
  }
};

// ─── UTILITIES ──────────────────────────────────────────────────────
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

function getMockJobs() {
  return [
    {
      id: '1',
      title: 'Senior Backend Engineer',
      role: 'Software Engineer',
      description: 'Build scalable APIs using Node.js and PostgreSQL. Experience with microservices and cloud platforms required.',
      num_questions: 4,
      duration_minutes: 60
    },
    {
      id: '2',
      title: 'Data Science Lead',
      role: 'Data Scientist',
      description: 'Lead ML projects using Python, TensorFlow, and cloud ML platforms. 5+ years experience required.',
      num_questions: 4,
      duration_minutes: 90
    },
    {
      id: '3',
      title: 'Frontend Developer',
      role: 'Software Engineer',
      description: 'Create responsive UIs with React, TypeScript, and modern CSS. Focus on performance and accessibility.',
      num_questions: 4,
      duration_minutes: 60
    }
  ];
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
      question: 'Design a scalable system architecture for a social media platform.',
      time_limit_seconds: 900
    },
    {
      type: 'code_debug',
      question: 'Fix the bug in this factorial function:',
      initial_code: `def factorial(n):\n  if n == 0:\n    return 1\n  return n * factorial(n)`,
      time_limit_seconds: 1200
    }
  ];
}

export default ApplicantDashboard;
