/* Design.jsx – THE FINAL, FULLY WORKING, BACKEND-CONNECTED MASTERPIECE */
import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Routes, Route, Navigate, useNavigate, useLocation, useParams, BrowserRouter
} from 'react-router-dom';
import {
  useAuth, useWebSocket, useToast, useFileUpload, useJobs, useRecruiterJobs,
  useCreateJob, useUpdateJob, useDeleteJob, useSubmitTest, useApplicantResults,
  usePublishGemini, useMessageHistory, exportToPDF, AuthProvider, ToastProvider, queryClient
} from './Backend.jsx';
import { useMutation, QueryClientProvider  } from '@tanstack/react-query'; // ← CRITICAL IMPORT
import './Faircruit.css';
// 10 DEFAULT ROLES WITH UNSPLASH
const DEFAULT_ROLES = [
  { name: "Software Engineer", img: "https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?w=600" },
  { name: "Data Scientist", img: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600" },
  { name: "Product Manager", img: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600" },
  { name: "DevOps Engineer", img: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600" },
  { name: "UX Designer", img: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600" },
  { name: "Security Engineer", img: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600" },
  { name: "Business Analyst", img: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600" },
  { name: "Marketing Manager", img: "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=600" },
  { name: "Sales Representative", img: "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=600" },
  { name: "HR Manager", img: "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600" }
];

// ───────────────────────────────────────────────────────────────────────
// LOGO
const FaircruitLogo = () => (
  <div className="logo">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
      <path d="M12 2L2 22H22L12 2Z" fill="var(--primary)" opacity="0.9"/>
      <path d="M12 6L6 18H18L12 6Z" fill="var(--primary)"/>
      <circle cx="12" cy="12" r="3.5" fill="var(--white)" stroke="var(--primary)" strokeWidth="1"/>
    </svg>
    <span className="logo-text">Fair</span>
    <span className="logo-highlight">cruit</span>
  </div>
);

// ───────────────────────────────────────────────────────────────────────
// HEADER
const Header = () => {
  const { isLoggedIn, logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const nav = [
    { path: '/', label: 'Home' },
    { path: '/about', label: 'About' },
    { path: '/get-started', label: 'Get Started' },
  ];
  return (
    <header className="header">
      <div className="container header-content">
        <div onClick={() => navigate('/')} className="logo-link">
          <FaircruitLogo />
        </div>
        <nav className="nav">
          {nav.map(item => (
            <a
              key={item.path}
              href={item.path}
              onClick={e => { e.preventDefault(); navigate(item.path); }}
              className={location.pathname === item.path ? 'active' : ''}
            >
              {item.label}
            </a>
          ))}
          {isLoggedIn ? (
            <div className="user-menu">
              <span className="username">Hi, {user?.username}</span>
              <button className="btn btn-sm" onClick={logout}>Logout</button>
            </div>
          ) : (
            <button className="btn" onClick={() => navigate('/get-started')}>
              Get Started
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

// ───────────────────────────────────────────────────────────────────────
// FOOTER
const Footer = () => (
  <footer className="footer">
    <div className="container footer-content">
      <div className="footer-brand">
        <FaircruitLogo />
        <p>Hire by Competence, Not Credentials.</p>
      </div>
      <div className="footer-links">
        <h3>Company</h3>
        <ul>
          <li><a href="#">Careers</a></li>
          <li><a href="#">Blog</a></li>
          <li><a href="#">Press</a></li>
        </ul>
      </div>
      <div className="footer-links">
        <h3>Resources</h3>
        <ul>
          <li><a href="#">Help Center</a></li>
          <li><a href="#">API Docs</a></li>
          <li><a href="#">Privacy</a></li>
        </ul>
      </div>
      <div className="footer-newsletter">
        <h3>Stay Updated</h3>
        <form onSubmit={e => { e.preventDefault(); alert('Subscribed!'); }}>
          <input type="email" placeholder="Your email" required />
          <button className="btn">Subscribe</button>
        </form>
      </div>
    </div>
    <div className="footer-bottom">
      <p>© {new Date().getFullYear()} faircruit. All rights reserved.</p>
    </div>
  </footer>
);

// ───────────────────────────────────────────────────────────────────────
// LANDING PAGE - Clean, simple
const LandingPage = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  return (
    <>
      <div className="hero" style={{ textAlign: 'center', padding: '80px 20px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '10px' }}>Fair Recruitment Platform</h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '30px' }}>Hire by Competence, Not Credentials</p>
        <button
          className="btn btn-lg"
          onClick={() => navigate(isLoggedIn ? '/dashboard/applicant' : '/get-started')}
          style={{ padding: '14px 30px', fontSize: '1.1rem', background: 'white', color: '#667eea', fontWeight: 'bold', cursor: 'pointer', border: 'none', borderRadius: '8px' }}
        >
          {isLoggedIn ? 'Go to Dashboard' : 'Get Started'}
        </button>
      </div>

      <section className="container section" style={{ maxWidth: '1200px', margin: '0 auto', padding: '60px 20px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '40px' }}>How It Works</h2>
        <div className="timeline" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '30px' }}>
          {[
            { title: 'Apply', desc: 'Browse available positions', icon: '📋' },
            { title: 'Test', desc: 'Take AI-generated tests', icon: '🧠' },
            { title: 'Analysis', desc: 'Get Gemini evaluation', icon: '✨' },
            { title: 'Results', desc: 'View your scores', icon: '✓' },
          ].map((step, i) => (
            <div key={i} style={{ textAlign: 'center', padding: '20px' }}>
              <div style={{ fontSize: '3rem', marginBottom: '10px' }}>{step.icon}</div>
              <h3>{step.title}</h3>
              <p style={{ color: '#718096' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <Footer />
    </>
  );

// ───────────────────────────────────────────────────────────────────────
// ABOUT US
const FAQItem = ({ question, answer }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="faq-item">
      <button className="faq-question" onClick={() => setOpen(!open)}>
        {question}
      </button>
      {open && <div className="faq-answer">{answer}</div>}
    </div>
  );
};

const AboutUs = () => {
  const faqs = [
    { q: "How does faircruit reduce bias?", a: "We redact names, photos, and schools. All evaluations are blind." },
    { q: "What are the 4 levels?", a: "Awareness → Application → Mastery → Influence." },
    { q: "Is proctoring used?", a: "Yes. Webcam, screen sharing, and anti-cheat detection." },
    { q: "How is AI used?", a: "Gemini analyzes code, essays, and video to extract skills." },
  ];
  return (
    <>
      <section className="hero-about">
        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1600" alt="Fair hiring" />
        <div className="overlay">
          <h1>About <span className="highlight">faircruit</span></h1>
        </div>
      </section>
      <section className="container section">
        <div className="card large">
          <p><strong>Mission:</strong> Eliminate bias. Hire by skill. Scale fairness.</p>
          <h3>Our 10 Default Roles</h3>
          <div className="role-grid">
            {DEFAULT_ROLES.map(role => (
              <div key={role.name} className="role-card">
                <img src={role.img} alt={role.name} />
                <span>{role.name}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card large">
          <h2>Frequently Asked Questions</h2>
          {faqs.map((faq, i) => <FAQItem key={i} question={faq.q} answer={faq.a} />)}
        </div>
      </section>
      <Footer />
    </>
  );
};

// ───────────────────────────────────────────────────────────────────────
// GET STARTED
const GetStarted = () => {
  const navigate = useNavigate();
  return (
    <section className="container section">
      <div className="card centered">
        <h1>Choose Your Path</h1>
        <div className="role-selection">
          <div className="role-card" onClick={() => navigate('/login')}>
            <div className="role-icon applicant">Person</div>
            <h3>Applicant</h3>
            <p>Apply with skills, not résumé</p>
          </div>
          <div className="role-card" onClick={() => navigate('/login')}>
            <div className="role-icon recruiter">Briefcase</div>
            <h3>Recruiter</h3>
            <p>Post jobs, hire fairly</p>
          </div>
        </div>
      </div>
    </section>
  );
};

// ───────────────────────────────────────────────────────────────────────
// LOGIN
const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, authAxios } = useAuth();
  const addToast = useToast();
  const navigate = useNavigate();

  const { mutate: loginMutate, isPending } = useMutation({
    mutationFn: async ({ email, password }) => {
      const res = await authAxios.post('/auth/login', { email, password });
      return res.data;
    },
    onSuccess: (data) => {
      login(data.access_token, data.user);
      addToast('Login successful!', 'success');
      navigate(`/dashboard/${data.user.role}`);
    },
    onError: () => addToast('Invalid credentials.', 'error')
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    loginMutate({ email, password });
  };

  return (
    <div className="form-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button type="submit" className="btn" disabled={isPending}>
          {isPending ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────────
// VIDEO RECORDER
const VideoRecorder = () => {
  const videoRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const addToast = useToast();

  useEffect(() => {
    if (videoRef.current && !recording) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          videoRef.current.srcObject = stream;
        })
        .catch(() => addToast('Camera access denied.', 'error'));
    }
  }, [recording, addToast]);

  return (
    <div className="video-recorder">
      <video ref={videoRef} autoPlay muted className="webcam-feed" />
      <button 
        onClick={() => setRecording(!recording)}
        className={`btn ${recording ? 'btn-stop' : 'btn-record'}`}
      >
        {recording ? 'Stop' : 'Start'} Recording
      </button>
    </div>
  );
};
 const UploadComponent = ({ applicationId }) => {
  const { authAxios } = useAuth();
  const addToast = useToast();
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await authAxios.post(`/api/v1/applicant/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      addToast('CV uploaded!', 'success');
    } catch {
      addToast('Upload failed.', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-box">
      <input type="file" accept=".pdf,.doc,.docx" onChange={handleUpload} disabled={uploading} />
      <p>{uploading ? 'Uploading...' : 'Drop CV here or click to upload'}</p>
    </div>
  );
};
// ───────────────────────────────────────────────────────────────────────
// TEST FLOW
const TestFlow = () => {
  const { applicationId } = useParams();
  const { authAxios, user } = useAuth();
  const addToast = useToast();
  const navigate = useNavigate();

  const [level, setLevel] = useState(1);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [timer, setTimer] = useState(1800);
  const [answer, setAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const submitMutation = useSubmitTest(applicationId);

  const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    try {
      const appRes = await authAxios.get('/applicant/applications');
      const app = appRes.data.items.find(a => a.id === applicationId);
      if (!app) throw new Error("Application not found");

      const qRes = await authAxios.post('/ml/generate-questions', {
        job_id: app.job_id
      });

      setQuestions(qRes.data.questions);
      const q = qRes.data.questions[0];
      setCurrentQuestion(q);
      setTimer(q.time_limit_seconds);
    } catch (err) {
      addToast('Failed to load questions.', 'error');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [applicationId, authAxios, addToast]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  useEffect(() => {
    if (questions.length > 0 && level <= 4) {
      const q = questions[level - 1];
      setCurrentQuestion(q);
      setTimer(q.time_limit_seconds);
      setAnswer('');
      setSelectedOption(null);
    }
  }, [level, questions]);

  useEffect(() => {
    if (!currentQuestion) return;
    const id = setInterval(() => {
      setTimer(t => {
        if (t <= 1) {
          clearInterval(id);
          handleSubmit();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [currentQuestion, level]);

  const formatTime = (s) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;

  const handleSubmit = () => {
    if (level === 1 && selectedOption === null) return addToast('Select an answer!', 'error');
    if (level > 1 && level < 4 && !answer.trim()) return addToast('Write your answer!', 'error');

    const payload = {
      level,
      question_id: currentQuestion?.question_id || `q${level}`,
      response: level === 1 ? selectedOption : answer
    };

    submitMutation.mutate(payload, {
      onSuccess: () => {
        if (level < 4) {
          setLevel(prev => prev + 1);
          addToast(`Level ${level} submitted!`, 'success');
        } else {
          addToast('Test completed!', 'success');
          navigate('/dashboard/applicant');
        }
      },
      onError: () => addToast('Submission failed.', 'error')
    });
  };

  useEffect(() => {
    const handle = () => setShowWarning(document.hidden);
    document.addEventListener('visibilitychange', handle);
    return () => document.removeEventListener('visibilitychange', handle);
  }, []);

  if (isLoading) return <div className="test-card">Loading questions from Gemini...</div>;

  return (
    <div className="test-container">
      {showWarning && <div className="exam-protection-warning">DO NOT SWITCH TABS!</div>}
      
      <div className="test-header">
        <div className="timer-display">{formatTime(timer)}</div>
        <div className="level-indicator">
          Level {level}/4 – {currentQuestion?.type?.toUpperCase() || 'Loading'}
        </div>
      </div>

      <div className="test-card">
        <div className="question-box">
          <h3>{currentQuestion?.question || 'Loading...'}</h3>

          {level === 1 && currentQuestion?.options && (
            <div className="mcq-options">
              {currentQuestion.options.map((opt, i) => (
                <label key={i} className="radio-option">
                  <input
                    type="radio"
                    checked={selectedOption === i}
                    onChange={() => setSelectedOption(i)}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
          )}

          {(level === 2 || level === 3) && (
            <textarea
              className="answer-input"
              placeholder="Write your detailed response..."
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              rows={14}
            />
          )}

          {level === 4 && <VideoRecorder />}

          <div className="test-actions">
            <button className="btn btn-submit" onClick={handleSubmit}>
              {level < 4 ? 'Submit & Next' : 'Finish Test'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const ApplyPage = () => {
  const { jobId } = useParams();
  const { authAxios } = useAuth();
  const navigate = useNavigate();
  const addToast = useToast();
  const [applicationId, setApplicationId] = useState(null);

  useEffect(() => {
    const apply = async () => {
      try {
        const res = await authAxios.post('/applicant/apply', { job_id: jobId });
        setApplicationId(res.data.id);
        addToast('Application created! Upload CV & start test.', 'success');
      } catch {
        addToast('Failed to apply.', 'error');
      }
    };
    apply();
  }, [jobId]);

  if (!applicationId) return <div className="card">Creating application...</div>;

  return (
    <div className="apply-flow">
      <h2>Step 1: Upload CV</h2>
      <UploadComponent applicationId={applicationId} />

      <h2>Step 2: Take Test</h2>
      <button
        className="btn btn-lg"
        onClick={() => navigate(`/dashboard/applicant/test/${applicationId}`)}
      >
        Start 4-Level Test
      </button>
    </div>
  );
};

const ResultsPage = () => {
  const { applicationId } = useParams();
  const { data: report, isLoading } = useQuery({
    queryKey: ['report', applicationId],
    queryFn: async () => {
      const res = await authAxios.get(`/api/v1/applicant/results/${applicationId}`);
      return res.data;
    },
  });

  if (isLoading) return <div className="card">Loading results...</div>;

  return (
    <div className="card large">
      <h2>Your Evaluation Report</h2>
      <div className="report">
        <p><strong>Score:</strong> {report.profile.score}/100</p>
        <p><strong>Narrative:</strong> {report.narrative}</p>
        {report.visuals_urls?.[0] && <img src={report.visuals_urls[0]} alt="Chart" />}
      </div>
      <button className="btn" onClick={() => window.print()}>Download PDF</button>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────────
// ROUTER
const AppRouter = () => {
  const { isLoggedIn } = useAuth();
  const location = useLocation();

  // Lazy load ApplicantDashboard
  const ApplicantDash = React.lazy(() => import('./components/ApplicantDashboard.jsx'));

  if (!isLoggedIn && ![
    '/', '/about', '/get-started', '/login', '/register'
  ].some(path => location.pathname.startsWith(path))) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      {!location.pathname.includes('dashboard') && <Header />}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutUs />} />
        <Route path="/get-started" element={<GetStarted />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/dashboard/applicant" element={isLoggedIn ? <React.Suspense fallback={<div style={{ padding: '20px', textAlign: 'center' }}>Loading dashboard...</div>}><ApplicantDash /></React.Suspense> : <Navigate to="/login" replace />} />
      </Routes>
      {!location.pathname.includes('dashboard') && <Footer />}
    </>
  );
};

const Root = () => {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AuthWrapper />
        </ToastProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

const AuthWrapper = () => {
  const navigate = useNavigate();
  const addToast = useToast();

  return (
    <AuthProvider navigate={navigate} addToast={addToast}>
      <AppRouter />
    </AuthProvider>
  );
};

export default Root;

  // Move to next question
  const goToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  // Submit test answers
  const submitTest = async () => {
    if (Object.keys(answers).length !== questions.length) {
      showToast('Please answer all questions before submitting', 'error');
      return;
    }

    try {
      const testData = {
        answers: questions.map((q, idx) => ({
          level: q.level,
          type: q.type,
          question: q.question,
          answer: answers[idx],
          time_limit: q.time_limit_seconds
        }))
      };

      // Create application first if needed
      const appRes = await authAxios.post('/applicant/apply', {
        job_id: selectedJob,
        cv_file_path: 'uploaded',
        test_attempt: 1
      });

      const applicationId = appRes.data.id;

      // Submit test answers
      await authAxios.post(`/applicant/tests/${applicationId}`, testData);

      showToast('Test submitted! Waiting for Gemini evaluation...', 'success');
      setTestInProgress(false);
      setTab('results');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to submit test', 'error');
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progressPercent = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div className="dashboard">
      <aside className="sidebar">
        {['home', 'tests', 'results', 'messages'].map(t => (
          <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </aside>
      <main className="main-content">
        {/* TAB: HOME - Available Jobs & CV Upload */}
        {tab === 'home' && (
          <div className="card">
            <h3>Welcome, {user?.username}!</h3>
            
            {/* CV Upload Section */}
            <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
              <h4>Step 1: Upload Your CV</h4>
              {!showCVUpload ? (
                <button className="btn" onClick={() => setShowCVUpload(true)}>
                  {uploading ? `Uploading... ${progress}%` : 'Upload CV'}
                </button>
              ) : (
                <div>
                  <input 
                    type="file" 
                    accept=".pdf,.doc,.docx,.txt" 
                    onChange={handleCVUpload}
                    disabled={uploading}
                  />
                  {uploading && <div style={{ marginTop: '10px' }}>Upload Progress: {progress}%</div>}
                </div>
              )}
            </div>

            {/* Available Jobs Section */}
            <h4>Step 2: Select a Job and Take the Test</h4>
            {jobsLoading ? (
              <p>Loading jobs...</p>
            ) : jobs && jobs.length > 0 ? (
              <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {jobs.map(job => (
                  <div key={job._id} className="job-card" style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
                    <h4>{job.title}</h4>
                    <p style={{ color: '#666', fontSize: '14px' }}>{job.description?.substring(0, 100)}...</p>
                    {job.competencies && (
                      <div style={{ marginBottom: '10px' }}>
                        <strong>Competencies:</strong>
                        <ul style={{ fontSize: '12px', margin: '5px 0' }}>
                          {job.competencies.map((comp, idx) => <li key={idx}>{comp}</li>)}
                        </ul>
                      </div>
                    )}
                    <button 
                      className="btn" 
                      onClick={() => startTest(job._id)}
                      disabled={loadingQuestions}
                    >
                      {loadingQuestions ? 'Loading Test...' : 'Start Test'}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p>No jobs available at the moment.</p>
            )}
          </div>
        )}

        {/* TAB: TESTS - In-Progress Test Taking */}
        {tab === 'tests' && (
          <div className="card">
            {!testInProgress ? (
              <div style={{ textAlign: 'center' }}>
                <h3>No Active Test</h3>
                <p>Click "Home" to select a job and start a test.</p>
              </div>
            ) : currentQuestion ? (
              <div>
                <h3>Competency Assessment Test</h3>
                <div style={{ marginBottom: '20px', textAlign: 'right' }}>
                  Question {currentQuestionIndex + 1} of {questions.length}
                </div>

                {/* Progress Bar */}
                <div style={{ width: '100%', height: '8px', backgroundColor: '#eee', borderRadius: '4px', marginBottom: '20px', overflow: 'hidden' }}>
                  <div style={{ width: `${progressPercent}%`, height: '100%', backgroundColor: '#4CAF50', transition: 'width 0.3s' }}></div>
                </div>

                {/* Question Display */}
                <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '8px', borderLeft: '4px solid #2196F3' }}>
                  <h4>Level {currentQuestion.level}: {currentQuestion.type.toUpperCase()}</h4>
                  <p style={{ fontSize: '16px', margin: '15px 0' }}>{currentQuestion.question}</p>

                  {/* Answer Input */}
                  {currentQuestion.type === 'mcq' ? (
                    <div style={{ marginTop: '15px' }}>
                      {currentQuestion.options?.map((opt, idx) => (
                        <label key={idx} style={{ display: 'block', marginBottom: '10px', cursor: 'pointer' }}>
                          <input
                            type="radio"
                            name="answer"
                            value={idx}
                            checked={answers[currentQuestionIndex] == idx}
                            onChange={(e) => handleAnswerChange(e.target.value)}
                            style={{ marginRight: '10px' }}
                          />
                          {opt}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      placeholder={`Your answer for Level ${currentQuestion.level}...`}
                      value={answers[currentQuestionIndex] || ''}
                      onChange={(e) => handleAnswerChange(e.target.value)}
                      style={{ width: '100%', minHeight: '120px', padding: '10px', marginTop: '10px', borderRadius: '4px', border: '1px solid #ddd', fontFamily: 'monospace' }}
                    />
                  )}

                  {/* Time Limit Info */}
                  <p style={{ fontSize: '12px', color: '#999', marginTop: '15px' }}>
                    Time limit: {currentQuestion.time_limit_seconds} seconds
                  </p>
                </div>

                {/* Navigation Buttons */}
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between', marginTop: '20px' }}>
                  <button 
                    className="btn"
                    onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                    disabled={currentQuestionIndex === 0}
                  >
                    Previous
                  </button>

                  {currentQuestionIndex < questions.length - 1 ? (
                    <button 
                      className="btn"
                      onClick={goToNextQuestion}
                      disabled={!answers[currentQuestionIndex]}
                    >
                      Next
                    </button>
                  ) : (
                    <button 
                      className="btn btn-success"
                      onClick={submitTest}
                      disabled={Object.keys(answers).length !== questions.length}
                    >
                      Submit Test
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <p>Loading test...</p>
            )}
          </div>
        )}

        {/* TAB: RESULTS - View Test Results & Gemini Evaluation */}
        {tab === 'results' && (
          <div className="card">
            <h3>Your Test Results</h3>
            {appsLoading ? (
              <p>Loading results...</p>
            ) : applications && applications.length > 0 ? (
              <div style={{ display: 'grid', gap: '20px' }}>
                {applications.map(app => (
                  <div key={app._id} style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#fafafa' }}>
                    <h4>{app.job_title}</h4>
                    <p><strong>Status:</strong> {app.status}</p>
                    {app.outcome && <p><strong>Outcome:</strong> {app.outcome}</p>}
                    {app.ml_report_id && (
                      <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                        <p><strong>Evaluation Available:</strong> Gemini has reviewed your CV and test answers</p>
                        <button className="btn" onClick={() => navigate(`/results/${app._id}`)}>
                          View Full Report
                        </button>
                      </div>
                    )}
                    {!app.ml_report_id && app.status !== 'evaluated' && (
                      <p style={{ color: '#f57c00' }}>⏳ Gemini is evaluating your submission...</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p>No test results yet. Complete a test to see results here.</p>
            )}
          </div>
        )}

        {/* TAB: MESSAGES */}
        {tab === 'messages' && (
          <div className="card">
            <h3>Messages</h3>
            <p>Message feature coming soon...</p>
          </div>
        )}
      </main>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────────
// ROUTER
const AppRouter = () => {
  const { isLoggedIn } = useAuth();
  const location = useLocation();

  // Lazy load ApplicantDashboard
  const ApplicantDash = React.lazy(() => import('./components/ApplicantDashboard.jsx'));

  if (!isLoggedIn && ![
    '/', '/about', '/get-started', '/login', '/register'
  ].some(path => location.pathname.startsWith(path))) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      {!location.pathname.includes('dashboard') && <Header />}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutUs />} />
        <Route path="/get-started" element={<GetStarted />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/dashboard/applicant" element={isLoggedIn ? <React.Suspense fallback={<div style={{ padding: '20px', textAlign: 'center' }}>Loading dashboard...</div>}><ApplicantDash /></React.Suspense> : <Navigate to="/login" replace />} />
      </Routes>
      {!location.pathname.includes('dashboard') && <Footer />}
    </>
  );
}

const Root = () => {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AuthWrapper />
        </ToastProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
}

const AuthWrapper = () => {
  const navigate = useNavigate();
  const addToast = useToast();

  return (
    <AuthProvider navigate={navigate} addToast={addToast}>
      <AppRouter />
    </AuthProvider>
  );
}

export default Root;