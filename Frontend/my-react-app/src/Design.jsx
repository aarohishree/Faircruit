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
      <div className="hero" style={{
        backgroundImage: 'linear-gradient(135deg, rgba(102, 126, 234, 0.85) 0%, rgba(118, 75, 162, 0.85) 100%), url("https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        textAlign: 'center',
        padding: '120px 20px',
        color: 'white',
        minHeight: '500px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <h1 style={{ fontSize: '3.5rem', marginBottom: '15px', fontWeight: 'bold', textShadow: '2px 2px 8px rgba(0,0,0,0.3)' }}>Fair Recruitment Platform</h1>
        <p style={{ fontSize: '1.3rem', marginBottom: '40px', textShadow: '1px 1px 4px rgba(0,0,0,0.3)' }}>Hire by Competence, Not Credentials</p>
        <button
          className="btn btn-lg"
          onClick={() => navigate(isLoggedIn ? '/dashboard/applicant' : '/get-started')}
          style={{ padding: '16px 36px', fontSize: '1.1rem', background: 'white', color: '#667eea', fontWeight: 'bold', cursor: 'pointer', border: 'none', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.2)', transition: 'transform 0.2s' }}
          onMouseOver={e => e.target.style.transform = 'scale(1.05)'}
          onMouseOut={e => e.target.style.transform = 'scale(1)'}
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
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, authAxios } = useAuth();
  const addToast = useToast();
  const navigate = useNavigate();

  const { mutate: loginMutate, isPending } = useMutation({
    mutationFn: async ({ email, password }) => {
      console.log('🔐 Attempting login with email:', email);
      try {
        const res = await authAxios.post('/auth/login', { email, password });
        console.log('✅ Login response received:', res.data);
        return res.data;
      } catch (err) {
        if (err.response) {
          // Backend error
          console.error('❌ Login error:', err.response.data);
          throw new Error(err.response.data.detail || 'Login failed');
        } else {
          // Network or unknown error
          console.error('❌ Login error:', err.message);
          throw new Error('Network error or backend not running');
        }
      }
    },
    onSuccess: (data) => {
      try {
        console.log('✅ onSuccess triggered, data:', data);
        login(data.access_token, data.user);
        console.log('✅ login() called');
        addToast('Login successful!', 'success');
        console.log('📍 About to navigate to:', `/dashboard/${data.user.role}`);
        navigate(`/dashboard/${data.user.role}`);
      } catch (e) {
        console.error('❌ Error after login success:', e);
        addToast('Login succeeded but frontend error occurred.', 'error');
      }
    },
    onError: (err) => {
      console.error('❌ onError triggered:', err);
      addToast(err.message || 'Invalid credentials.', 'error');
    }
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
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            name="email"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            name="password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn" disabled={isPending}>
          {isPending ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────────
// MAIN ROUTING
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
        <Route path="/" element={<><LandingPage /><Footer /></>} />
        <Route path="/about" element={<><AboutUs /><Footer /></>} />
        <Route path="/get-started" element={<><GetStarted /><Footer /></>} />
        <Route path="/login" element={<><LoginForm /><Footer /></>} />
        <Route 
          path="/dashboard/applicant" 
          element={isLoggedIn ? (
            <React.Suspense fallback={<div style={{ padding: '20px', textAlign: 'center' }}>Loading dashboard...</div>}>
              <ApplicantDash />
            </React.Suspense>
          ) : (
            <Navigate to="/login" replace />
          )} 
        />
      </Routes>
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
