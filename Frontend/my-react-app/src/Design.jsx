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
// LANDING PAGE
const LandingPage = () => {
  const navigate = useNavigate();
  return (
    <>
      <section className="hero">
        <div className="hero-bg">
          <img src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1600" alt="Team collaboration" />
        </div>
        <div className="container hero-content">
          <h1>Hire by <span className="highlight">Competence</span>,<br/>Not Credentials.</h1>
          <p className="hero-subtitle">
            AI-powered, bias-reduced hiring with structured 4-level tests and LLM analysis.
          </p>
          <div className="cta-group">
            <button className="btn btn-lg" onClick={() => navigate('/get-started')}>
              Start as Applicant
            </button>
            <button className="btn btn-outline btn-lg" onClick={() => navigate('/get-started')}>
              Post a Job
            </button>
          </div>
        </div>
      </section>
      <section className="container section">
        <h2>How It Works</h2>
        <div className="timeline">
          {[
            { title: 'Upload & Assess', desc: 'Submit evidence and complete structured tests.', img: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=400' },
            { title: 'AI Analyze', desc: 'LLMs extract skills and generate competency vectors.', img: 'https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400' },
            { title: 'Hire Fairly', desc: 'Review objective scores and ML reports.', img: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400' },
          ].map((step, i) => (
            <div key={i} className="timeline-item">
              <img src={step.img} alt={step.title} className="timeline-img" />
              <div className="timeline-icon">{i + 1}</div>
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>
      <Footer />
    </>
  );
};

// ───────────────────────────────────────────────────────────────────────
// ABOUT US
const FAQItem = ({ question, answer }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="faq-item">
      <button className="faq-question" onClick={() => setOpen(!open)}>
        {question}
        <span className={`arrow ${open ? 'open' : ''}`}>Down Arrow</span>
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
      const res = await authAxios.post('/api/v1/auth/login', { email, password });
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
      const appRes = await authAxios.get('/api/v1/applicant/applications');
      const app = appRes.data.items.find(a => a.id === applicationId);
      if (!app) throw new Error("Application not found");

      const qRes = await authAxios.post('/api/v1/ml/generate-questions', {
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
        const res = await authAxios.post('/api/v1/applicant/apply', { job_id: jobId });
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
// APPLICANT DASHBOARD
const ApplicantDashboard = () => {
  const [tab, setTab] = useState('home');
  const { data: jobs } = useJobs();
  const navigate = useNavigate();

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
        {tab === 'home' && (
          <div className="card">
            <h3>Available Jobs</h3>
            <div className="grid">
              {jobs?.map(job => (
                <div key={job.id} className="job-card">
                  <h4>{job.title}</h4>
                  <button className="btn" onClick={() => navigate(`/dashboard/applicant/apply/${job.id}`)}>
                    Start Test
                  </button>
                </div>
              ))}
            </div>
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
  const navigate = useNavigate();

  if (!isLoggedIn && !['/', '/about', '/get-started', '/login', '/register'].includes(location.pathname)) {
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
        <Route path="/dashboard/applicant" element={<ApplicantDashboard />} />
        <Route path="/dashboard/applicant/test/:applicationId" element={<TestFlow />} />
        <Route path="/dashboard/applicant/apply/:jobId" element={<ApplyPage />} />
        <Route path="/dashboard/applicant/results/:applicationId" element={<ResultsPage />} />
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