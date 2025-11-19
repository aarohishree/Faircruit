/* 
COMPLETE ENHANCED DESIGN.JSX WITH ALL FEATURES:
- Job Listings Page
- Advanced Test Taking with Code Editor
- Anti-Cheat Features
- Timer Management
- MCQ, Short Answer, Essay, Code Debugging Questions
- Webcam Monitoring
- Comprehensive Job Details
*/

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Routes, Route, Navigate, useNavigate, useLocation, useParams, BrowserRouter
} from 'react-router-dom';
import {
  useAuth, useWebSocket, useToast, useFileUpload, useJobs, useRecruiterJobs,
  useCreateJob, useUpdateJob, useDeleteJob, useSubmitTest, useApplicantResults,
  usePublishGemini, useMessageHistory, exportToPDF, AuthProvider, ToastProvider, queryClient
} from './Backend.jsx';
import { useMutation, QueryClientProvider, useQuery } from '@tanstack/react-query';
import './Faircruit.css';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS & HELPERS
// ─────────────────────────────────────────────────────────────────────

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

// ─────────────────────────────────────────────────────────────────────
// CODE EDITOR COMPONENT
// ─────────────────────────────────────────────────────────────────────

const CodeEditor = ({ initialCode, onChange, readOnly = false }) => {
  const [code, setCode] = useState(initialCode || '');

  const handleChange = (e) => {
    setCode(e.target.value);
    onChange && onChange(e.target.value);
  };

  return (
    <div className="code-editor">
      <textarea
        value={code}
        onChange={handleChange}
        readOnly={readOnly}
        className="code-editor-textarea"
        spellCheck="false"
        style={{
          fontFamily: 'Monaco, Courier New, monospace',
          fontSize: '13px',
          lineHeight: '1.5',
          padding: '15px',
          backgroundColor: '#f5f5f5',
          border: '1px solid #ddd',
          borderRadius: '4px',
          minHeight: '300px',
          width: '100%',
          color: '#333'
        }}
      />
      <div style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
        Lines: {code.split('\n').length} | Characters: {code.length}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────
// ANTI-CHEAT MONITORING
// ─────────────────────────────────────────────────────────────────────

const AntiCheatMonitor = ({ onViolation }) => {
  const [violations, setViolations] = useState(0);
  const videoRef = useRef(null);
  const [webcamActive, setWebcamActive] = useState(false);

  useEffect(() => {
    // Tab switching detection
    const handleVisibilityChange = () => {
      if (document.hidden) {
        const newViolations = violations + 1;
        setViolations(newViolations);
        onViolation && onViolation({
          type: 'tab_switch',
          count: newViolations,
          timestamp: new Date()
        });
      }
    };

    // Right-click detection (disable copy-paste)
    const handleContextMenu = (e) => {
      e.preventDefault();
      const newViolations = violations + 1;
      setViolations(newViolations);
      onViolation && onViolation({
        type: 'copy_paste_attempt',
        count: newViolations,
        timestamp: new Date()
      });
    };

    // Keyboard shortcuts detection (F12, Ctrl+Shift+I, etc.)
    const handleKeyDown = (e) => {
      if (
        e.keyCode === 123 ||
        (e.ctrlKey && e.shiftKey && e.keyCode === 73) ||
        (e.ctrlKey && e.shiftKey && e.keyCode === 75) ||
        (e.metaKey && e.altKey && e.keyCode === 73)
      ) {
        e.preventDefault();
        const newViolations = violations + 1;
        setViolations(newViolations);
        onViolation && onViolation({
          type: 'developer_tools',
          count: newViolations,
          timestamp: new Date()
        });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [violations, onViolation]);

  // Webcam monitoring
  useEffect(() => {
    if (webcamActive) {
      navigator.mediaDevices.getUserMedia({ video: { width: 200, height: 150 } })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch(err => console.error('Webcam access denied:', err));
    }
  }, [webcamActive]);

  return (
    <div style={{
      position: 'fixed',
      top: 10,
      right: 10,
      backgroundColor: 'white',
      border: '2px solid #f44336',
      borderRadius: '8px',
      padding: '15px',
      zIndex: 9999,
      maxWidth: '250px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
    }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#d32f2f' }}>🔒 Anti-Cheat Monitor</h4>
      
      <div style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#ffebee', borderRadius: '4px' }}>
        <p style={{ margin: '0', fontSize: '14px', color: '#d32f2f' }}>
          ⚠️ Violations: <strong>{violations}</strong>
        </p>
      </div>

      {violations > 0 && (
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
          <p style={{ margin: '5px 0' }}>🚫 Tab switches, copy attempts, or dev tools detected!</p>
          <p style={{ margin: '5px 0' }}>Multiple violations may affect your evaluation.</p>
        </div>
      )}

      <button
        onClick={() => setWebcamActive(!webcamActive)}
        style={{
          width: '100%',
          padding: '8px',
          backgroundColor: webcamActive ? '#4caf50' : '#2196f3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '12px',
          marginTop: '10px'
        }}
      >
        {webcamActive ? '📹 Webcam On' : '📹 Start Webcam'}
      </button>

      {webcamActive && (
        <div style={{ marginTop: '10px' }}>
          <video
            ref={videoRef}
            autoPlay
            muted
            style={{
              width: '100%',
              height: '120px',
              borderRadius: '4px',
              backgroundColor: '#000'
            }}
          />
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────
// LOGO & HEADER
// ─────────────────────────────────────────────────────────────────────

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

const Header = () => {
  const { isLoggedIn, logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const nav = [
    { path: '/', label: 'Home' },
    { path: '/about', label: 'About' },
    { path: '/jobs', label: 'Jobs' },
  ];
  return (
    <header className="header">
      <div className="container header-content">
        <div onClick={() => navigate('/')} className="logo-link" style={{ cursor: 'pointer' }}>
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
            <div className="user-menu" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <span className="username" style={{ fontSize: '14px' }}>Hi, {user?.username}</span>
              <button className="btn btn-sm" onClick={logout}>Logout</button>
            </div>
          ) : (
            <button className="btn" onClick={() => navigate('/login')}>
              Get Started
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

// ─────────────────────────────────────────────────────────────────────
// FOOTER
// ─────────────────────────────────────────────────────────────────────

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

// ─────────────────────────────────────────────────────────────────────
// JOB LISTINGS PAGE
// ─────────────────────────────────────────────────────────────────────

const JobListingsPage = () => {
  const navigate = useNavigate();
  const { authAxios } = useAuth();
  const addToast = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [page, setPage] = useState(1);

  const { data: jobsData, isLoading, error } = useQuery({
    queryKey: ['jobs', page, selectedRole, searchQuery],
    queryFn: async () => {
      const res = await authAxios.get('/applicant/jobs', {
        params: {
          page,
          size: 12,
          role: selectedRole || undefined,
          search: searchQuery || undefined
        }
      });
      return res.data;
    }
  });

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
    setPage(1);
  };

  const handleRoleFilter = (role) => {
    setSelectedRole(role);
    setPage(1);
  };

  if (error) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center', marginTop: '40px' }}>
          <h2 style={{ color: '#d32f2f' }}>Error Loading Jobs</h2>
          <p>Please try again later or contact support.</p>
          <button className="btn" onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{
        backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '60px 0',
        textAlign: 'center',
        color: 'white'
      }}>
        <div className="container">
          <h1 style={{ marginBottom: '20px' }}>Find Your Perfect Role</h1>
          <p style={{ fontSize: '18px', marginBottom: '40px' }}>
            Discover opportunities aligned with your skills, not your credentials
          </p>
          
          <div style={{
            display: 'flex',
            gap: '10px',
            maxWidth: '600px',
            margin: '0 auto',
            marginBottom: '30px'
          }}>
            <input
              type="text"
              placeholder="Search jobs by title or company..."
              value={searchQuery}
              onChange={handleSearch}
              style={{
                flex: 1,
                padding: '15px',
                borderRadius: '4px',
                border: 'none',
                fontSize: '14px'
              }}
            />
            <button className="btn" style={{ padding: '15px 30px' }}>Search</button>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
        {/* Role Filter */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ marginBottom: '20px' }}>Filter by Role</h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '10px'
          }}>
            <button
              onClick={() => handleRoleFilter('')}
              style={{
                padding: '10px 15px',
                backgroundColor: !selectedRole ? '#667eea' : '#f0f0f0',
                color: !selectedRole ? 'white' : '#333',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: !selectedRole ? 'bold' : 'normal'
              }}
            >
              All Roles
            </button>
            {DEFAULT_ROLES.map(role => (
              <button
                key={role.name}
                onClick={() => handleRoleFilter(role.name)}
                style={{
                  padding: '10px 15px',
                  backgroundColor: selectedRole === role.name ? '#667eea' : '#f0f0f0',
                  color: selectedRole === role.name ? 'white' : '#333',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: selectedRole === role.name ? 'bold' : 'normal'
                }}
              >
                {role.name}
              </button>
            ))}
          </div>
        </div>

        {/* Jobs Grid */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>Loading job opportunities...</p>
          </div>
        ) : jobsData?.items && jobsData.items.length > 0 ? (
          <>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
              gap: '25px',
              marginBottom: '40px'
            }}>
              {jobsData.items.map(job => (
                <div
                  key={job._id}
                  className="card"
                  style={{
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    borderLeft: '4px solid #667eea'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
                    e.currentTarget.style.transform = 'translateY(-5px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ marginBottom: '15px' }}>
                    <h3 style={{ margin: '0 0 5px 0' }}>{job.title}</h3>
                    <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                      {job.company || 'Company Name'}
                    </p>
                  </div>

                  <div style={{
                    display: 'flex',
                    gap: '10px',
                    marginBottom: '15px',
                    flexWrap: 'wrap'
                  }}>
                    {job.role && (
                      <span style={{
                        backgroundColor: '#e8eaf6',
                        color: '#667eea',
                        padding: '4px 10px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {job.role}
                      </span>
                    )}
                    {job.level && (
                      <span style={{
                        backgroundColor: '#f3e5f5',
                        color: '#764ba2',
                        padding: '4px 10px',
                        borderRadius: '20px',
                        fontSize: '12px'
                      }}>
                        {job.level}
                      </span>
                    )}
                  </div>

                  <p style={{
                    fontSize: '13px',
                    color: '#666',
                    marginBottom: '15px',
                    minHeight: '40px'
                  }}>
                    {job.description?.substring(0, 100)}...
                  </p>

                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingTop: '15px',
                    borderTop: '1px solid #e0e0e0'
                  }}>
                    <span style={{ fontSize: '12px', color: '#999' }}>
                      👥 {job.application_count || 0} applications
                    </span>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        className="btn btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/job/${job._id}`);
                        }}
                      >
                        View Details
                      </button>
                      <button
                        className="btn btn-sm"
                        style={{ backgroundColor: '#4caf50' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/apply/${job._id}`);
                        }}
                      >
                        Apply Now
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '10px',
              marginTop: '40px'
            }}>
              <button
                className="btn"
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                ← Previous
              </button>
              <span style={{ padding: '10px 15px' }}>
                Page {page} of {Math.ceil((jobsData?.total || 0) / 12)}
              </span>
              <button
                className="btn"
                disabled={!jobsData?.items || jobsData.items.length < 12}
                onClick={() => setPage(p => p + 1)}
              >
                Next →
              </button>
            </div>
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <h3>No jobs found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────
// JOB DETAILS PAGE
// ─────────────────────────────────────────────────────────────────────

const JobDetailsPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { authAxios } = useAuth();
  const addToast = useToast();

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      const res = await authAxios.get(`/applicant/jobs/${jobId}`);
      return res.data;
    }
  });

  if (isLoading) return <div className="container" style={{ marginTop: '40px' }}><p>Loading job details...</p></div>;
  if (!job) return <div className="container" style={{ marginTop: '40px' }}><p>Job not found</p></div>;

  return (
    <div>
      <div style={{
        backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '40px 0'
      }}>
        <div className="container">
          <button
            onClick={() => navigate('/jobs')}
            style={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: 'none',
              padding: '10px 15px',
              borderRadius: '4px',
              cursor: 'pointer',
              marginBottom: '20px'
            }}
          >
            ← Back to Jobs
          </button>
          <h1>{job.title}</h1>
          <p style={{ fontSize: '18px', opacity: 0.9 }}>{job.company || 'Company'}</p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '40px' }}>
          <div>
            <div className="card" style={{ marginBottom: '30px' }}>
              <h2>About This Role</h2>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', color: '#666' }}>
                {job.description}
              </div>
            </div>

            <div className="card">
              <h2>Assessment Structure</h2>
              <div style={{ backgroundColor: '#f5f5f5', padding: '20px', borderRadius: '8px' }}>
                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>📝 Level 1: Awareness (MCQ) - 2 minutes</h4>
                  <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                    Test your basic understanding with multiple-choice questions.
                  </p>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>✍️ Level 2: Application (Short Answer) - 10 minutes</h4>
                  <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                    Demonstrate practical application of your skills.
                  </p>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>🔬 Level 3: Analysis & Synthesis (Essay) - 15 minutes</h4>
                  <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                    Provide deep analysis and thoughtful insights.
                  </p>
                </div>
                <div>
                  <h4 style={{ margin: '0 0 10px 0' }}>💻 Level 4: Mastery (Code/Problem Solving) - 20 minutes</h4>
                  <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                    Solve real-world challenges and debug code.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="card" style={{ position: 'sticky', top: '20px' }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '15px'
              }}>
                <div>
                  <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#999', textTransform: 'uppercase' }}>Role</p>
                  <p style={{ margin: '0', fontSize: '16px', fontWeight: 'bold' }}>{job.role || 'Not specified'}</p>
                </div>
                <div>
                  <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#999', textTransform: 'uppercase' }}>Level</p>
                  <p style={{ margin: '0', fontSize: '16px', fontWeight: 'bold' }}>{job.level || 'Not specified'}</p>
                </div>
                <div>
                  <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#999', textTransform: 'uppercase' }}>Total Assessment Time</p>
                  <p style={{ margin: '0', fontSize: '16px', fontWeight: 'bold' }}>~47 minutes</p>
                </div>

                <button
                  className="btn"
                  style={{
                    width: '100%',
                    padding: '15px',
                    backgroundColor: '#4caf50',
                    marginTop: '20px',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                  onClick={() => navigate(`/apply/${jobId}`)}
                >
                  Apply Now
                </button>

                <div style={{
                  backgroundColor: '#fff3cd',
                  padding: '15px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#856404',
                  textAlign: 'center'
                }}>
                  ⏱️ Complete all 4 levels in one session
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────
// ADVANCED TEST FLOW WITH ALL FEATURES
// ─────────────────────────────────────────────────────────────────────

const AdvancedTestFlow = () => {
  const { applicationId } = useParams();
  const { authAxios, user } = useAuth();
  const addToast = useToast();
  const navigate = useNavigate();

  const [currentLevel, setCurrentLevel] = useState(1);
  const [questions, setQuestions] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [timeLeft, setTimeLeft] = useState(120);
  const [answers, setAnswers] = useState({});
  const [selectedOption, setSelectedOption] = useState(null);
  const [codeAnswer, setCodeAnswer] = useState('');
  const [textAnswer, setTextAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [violations, setViolations] = useState([]);
  const [testStarted, setTestStarted] = useState(false);

  const submitMutation = useSubmitTest(applicationId);

  // Load questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setIsLoading(true);
        const appRes = await authAxios.get('/applicant/applications');
        const app = appRes.data.items.find(a => a.id === applicationId);
        if (!app) throw new Error("Application not found");

        const qRes = await authAxios.post('/applicant/generate-questions/' + app.job_id);
        setQuestions(qRes.data.questions);
        setCurrentQuestion(qRes.data.questions['level_1']);
        setTimeLeft(qRes.data.questions['level_1'].time_limit_seconds);
      } catch (err) {
        addToast('Failed to load questions.', 'error');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadQuestions();
  }, [applicationId, authAxios, addToast]);

  // Timer effect
  useEffect(() => {
    if (!testStarted || !currentQuestion || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          handleNextQuestion();
          return currentQuestion.time_limit_seconds;
        }
        return t - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, testStarted, currentQuestion]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSubmit = () => {
    const levelKey = `level_${currentLevel}`;
    
    if (currentLevel === 1 && selectedOption === null) {
      addToast('Please select an answer', 'error');
      return;
    }
    if (currentLevel > 1 && !textAnswer.trim() && currentLevel !== 4) {
      addToast('Please provide an answer', 'error');
      return;
    }
    if (currentLevel === 4 && !codeAnswer.trim()) {
      addToast('Please provide code review/solution', 'error');
      return;
    }

    const answerData = {
      level: currentLevel,
      question_id: currentQuestion.question_id || `q${currentLevel}`,
      response: currentLevel === 1 ? selectedOption : (currentLevel === 4 ? codeAnswer : textAnswer),
      type: currentQuestion.type
    };

    setAnswers(prev => ({
      ...prev,
      [levelKey]: answerData
    }));

    if (currentLevel < 4) {
      handleNextQuestion();
    } else {
      handleSubmitTest();
    }
  };

  const handleNextQuestion = () => {
    if (currentLevel < 4) {
      setCurrentLevel(currentLevel + 1);
      const nextQuestion = questions[`level_${currentLevel + 1}`];
      setCurrentQuestion(nextQuestion);
      setTimeLeft(nextQuestion.time_limit_seconds);
      setSelectedOption(null);
      setTextAnswer('');
      setCodeAnswer('');
    }
  };

  const handleSubmitTest = () => {
    submitMutation.mutate(
      { answers: Object.values(answers), violations },
      {
        onSuccess: () => {
          addToast('Test submitted successfully!', 'success');
          navigate('/dashboard/applicant');
        },
        onError: () => addToast('Submission failed', 'error')
      }
    );
  };

  if (isLoading) {
    return <div className="container" style={{ textAlign: 'center', padding: '40px' }}><p>Generating AI questions...</p></div>;
  }

  return (
    <div className="test-container" style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', paddingTop: '20px', paddingBottom: '40px' }}>
      {/* Anti-Cheat Monitor */}
      <AntiCheatMonitor onViolation={(v) => setViolations(prev => [...prev, v])} />

      {/* Start Test Modal */}
      {!testStarted && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="card" style={{ maxWidth: '500px', padding: '40px', textAlign: 'center' }}>
            <h2>Ready to Start?</h2>
            <div style={{
              backgroundColor: '#fff3cd',
              padding: '20px',
              borderRadius: '8px',
              marginBottom: '20px',
              fontSize: '14px',
              color: '#856404'
            }}>
              <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>⚠️ Important:</p>
              <ul style={{ margin: '0', textAlign: 'left' }}>
                <li>Do not switch tabs or windows</li>
                <li>Enable webcam for proctoring</li>
                <li>You cannot copy/paste</li>
                <li>Developer tools are disabled</li>
                <li>Total time: ~47 minutes for all levels</li>
              </ul>
            </div>
            <button
              className="btn"
              style={{ width: '100%', padding: '15px', fontSize: '16px' }}
              onClick={() => setTestStarted(true)}
            >
              I Understand, Start Test
            </button>
          </div>
        </div>
      )}

      {testStarted && (
        <div className="container">
          {/* Test Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div>
              <h3 style={{ margin: '0', fontSize: '18px' }}>Level {currentLevel} / 4</h3>
              <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                {currentQuestion?.type?.toUpperCase() || 'LOADING'}
              </p>
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: timeLeft < 60 ? '#d32f2f' : '#667eea',
              fontFamily: 'monospace'
            }}>
              ⏱️ {formatTime(timeLeft)}
            </div>
            <div style={{
              display: 'flex',
              gap: '8px'
            }}>
              {[1, 2, 3, 4].map(l => (
                <div
                  key={l}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    color: 'white',
                    backgroundColor: l === currentLevel ? '#667eea' : (answers[`level_${l}`] ? '#4caf50' : '#ddd')
                  }}
                >
                  {l}
                </div>
              ))}
            </div>
          </div>

          {/* Question Content */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <h2 style={{ marginTop: '0' }}>{currentQuestion?.question}</h2>

            {/* MCQ */}
            {currentLevel === 1 && currentQuestion?.options && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {currentQuestion.options.map((option, idx) => (
                  <label
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '15px',
                      border: '2px solid ' + (selectedOption === idx ? '#667eea' : '#e0e0e0'),
                      borderRadius: '8px',
                      cursor: 'pointer',
                      backgroundColor: selectedOption === idx ? '#f3f4ff' : 'white',
                      transition: 'all 0.2s'
                    }}
                  >
                    <input
                      type="radio"
                      checked={selectedOption === idx}
                      onChange={() => setSelectedOption(idx)}
                      style={{ marginRight: '15px', width: '20px', height: '20px' }}
                    />
                    <span style={{ fontSize: '15px' }}>{option}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Short Answer / Essay */}
            {(currentLevel === 2 || currentLevel === 3) && (
              <div>
                <textarea
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  placeholder={currentLevel === 2 ? "Write your 2-3 sentence answer..." : "Write your detailed analysis..."}
                  style={{
                    width: '100%',
                    minHeight: currentLevel === 3 ? '400px' : '200px',
                    padding: '15px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    fontFamily: 'Arial, sans-serif',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
                <div style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
                  Words: {textAnswer.split(/\s+/).filter(w => w).length}
                </div>
              </div>
            )}

            {/* Code Review / Debug */}
            {currentLevel === 4 && (
              <div>
                <h4 style={{ marginBottom: '15px' }}>Code to Review:</h4>
                <CodeEditor
                  initialCode={currentQuestion?.initial_code}
                  readOnly={true}
                />

                <h4 style={{ marginTop: '30px', marginBottom: '15px' }}>Your Solution / Review:</h4>
                <CodeEditor
                  initialCode={codeAnswer}
                  onChange={setCodeAnswer}
                />
              </div>
            )}

            {/* Action Buttons */}
            <div style={{
              display: 'flex',
              gap: '10px',
              justifyContent: 'flex-end',
              marginTop: '30px',
              paddingTop: '20px',
              borderTop: '1px solid #e0e0e0'
            }}>
              <button
                className="btn"
                style={{ backgroundColor: '#f0f0f0', color: '#333' }}
                onClick={() => {
                  setSelectedOption(null);
                  setTextAnswer('');
                  setCodeAnswer('');
                }}
              >
                Clear Answer
              </button>
              <button
                className="btn"
                style={{ backgroundColor: currentLevel < 4 ? '#667eea' : '#4caf50' }}
                onClick={handleAnswerSubmit}
              >
                {currentLevel < 4 ? 'Next Level →' : '✓ Submit Test'}
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{
            width: '100%',
            height: '8px',
            backgroundColor: '#e0e0e0',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${(currentLevel / 4) * 100}%`,
              height: '100%',
              backgroundColor: '#667eea',
              transition: 'width 0.3s'
            }} />
          </div>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────
// ROUTES & EXPORTS
// ─────────────────────────────────────────────────────────────────────

export default AdvancedTestFlow;
