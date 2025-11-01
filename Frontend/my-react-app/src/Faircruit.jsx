import React, { useState, useEffect, useContext, createContext, useReducer, useCallback, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { z as Zod } from 'zod';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import './Faircruit.css';
const VITE_API_BASE = import.meta.env.VITE_API_BASE;
const VITE_WS_BASE = import.meta.env.VITE_WS_BASE;
const VITE_MAX_UPLOAD_SIZE_BYTES = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE_BYTES) || 5242880;
const VITE_ALLOWED_UPLOAD_MIMES = import.meta.env.VITE_ALLOWED_UPLOAD_MIMES || 'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,video/mp4';

const ALLOWED_MIMES_ARRAY = VITE_ALLOWED_UPLOAD_MIMES.split(',').map(m => m.trim());
const queryClient = new QueryClient();

const CompetencySchema = Zod.object({
    level: Zod.string().nonempty('Level is required'),
    description: Zod.string().min(1, 'Description is required'),
    evidence_type: Zod.string().nonempty('Evidence type is required')
});

const JobCreateSchema = Zod.object({
    title: Zod.string().min(3, 'Title must be at least 3 characters'),
    description: Zod.string().min(10, 'Description must be at least 10 characters'),
    competencies: Zod.array(CompetencySchema).min(1, 'At least one competency required'),
    evidence_types: Zod.array(Zod.string().nonempty()).min(1, 'At least one evidence type required'),
    duration_minutes: Zod.number().min(10, 'Duration must be at least 10 minutes'),
    criteria: Zod.string().min(10, 'Criteria must be at least 10 characters')
});

const ToastContext = createContext();

const useToast = () => useContext(ToastContext);

const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback((message, type = 'info', duration = 5000) => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => removeToast(id), duration);
    }, []);

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={addToast}>
            {children}
            <div className="toast-container">
                {toasts.map(toast => (
                    <div key={toast.id} className={`toast toast-${toast.type}`}>
                        {toast.message}
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};

// const authAxios = axios.create({
//     baseURL: VITE_API_BASE,
//     headers: { 'Content-Type': 'application/json' }
// });
export const authAxios = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  headers: { 'Content-Type': 'application/json' },
});


const AuthContext = createContext();

const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(null);
    const [user, setUser] = useState(null);
    const navigate = useContext(RouterContext).navigate;
    const addToast = useToast();

    useEffect(() => {
        const interceptor = authAxios.interceptors.request.use(config => {
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        }, error => Promise.reject(error));

        const responseInterceptor = authAxios.interceptors.response.use(
            response => response,
            async (error) => {
                const status = error.response?.status;
                if (status === 401) {
                    addToast("Session expired or unauthorized. Please log in again.", 'error');
                    setToken(null);
                    setUser(null);
                    navigate('/login');
                } else if (status === 403) {
                    addToast("Forbidden. You do not have permission to access this resource.", 'error');
                } else if (status === 429) {
                    addToast("Rate limit exceeded. Please try again later.", 'error');
                } else if (status === 502 || status === 503) {
                    addToast("Service temporarily unavailable. Please try again shortly.", 'error');
                }
                return Promise.reject(error);
            }
        );

        return () => {
            authAxios.interceptors.request.eject(interceptor);
            authAxios.interceptors.response.eject(responseInterceptor);
        };
    }, [token, navigate, addToast]);

    const login = (jwtToken, userData) => {
        setToken(jwtToken);
        setUser(userData);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        navigate('/login');
    };

    const isLoggedIn = !!token && !!user;
    const isAdmin = isLoggedIn && user.role === 'admin';
    const isRecruiter = isLoggedIn && user.role === 'recruiter';
    const isApplicant = isLoggedIn && user.role === 'applicant';

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isLoggedIn, isAdmin, isRecruiter, isApplicant, authAxios }}>
            {children}
        </AuthContext.Provider>
    );
};

const WSContext = createContext();

const useWS = () => useContext(WSContext);

const WSProvider = ({ children }) => {
    const { token, isLoggedIn, user, logout } = useAuth();
    const addToast = useToast();

    const [ws, setWs] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const [messageQueue, setMessageQueue] = useState([]);

    const wsRef = useRef(null);
    const retryTimeoutRef = useRef(null);
    const backoffTime = useRef(1000);

    const connect = useCallback(() => {
        if (!isLoggedIn || !user || wsRef.current) return;

        const newWs = new WebSocket(`${VITE_WS_BASE}/messages/${user.id}`);
        wsRef.current = newWs;
        setWs(newWs);

        newWs.onopen = () => {
            console.log('WS: Connection established. Sending auth token.');
            setIsConnected(true);
            backoffTime.current = 1000;
            newWs.send(JSON.stringify({ type: 'auth', token }));
        };

        newWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'auth_ok') {
                console.log('WS: Authentication successful. Draining queue.');
                setMessageQueue(prevQueue => {
                    prevQueue.forEach(msg => newWs.send(JSON.stringify(msg)));
                    return [];
                });
            } else if (data.type === 'new_message') {
                setMessages(prev => [...prev, { ...data.payload, id: data.payload._id }]);
            }
        };

        newWs.onclose = (event) => {
            console.log('WS: Disconnected. Code:', event.code);
            wsRef.current = null;
            setIsConnected(false);
            if (isLoggedIn) {
                addToast("WebSocket disconnected. Attempting reconnect...", 'warning');
                retryTimeoutRef.current = setTimeout(() => {
                    backoffTime.current = Math.min(32000, backoffTime.current * 2);
                    connect();
                }, backoffTime.current);
            }
        };

        newWs.onerror = (error) => {
            console.error('WS Error:', error);
            newWs.close();
        };
    }, [isLoggedIn, token, user, addToast]);

    useEffect(() => {
        if (isLoggedIn && user && !wsRef.current) {
            connect();
        } else if (!isLoggedIn && wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
            clearTimeout(retryTimeoutRef.current);
        }
    }, [isLoggedIn, user, connect]);

    const sendMessage = useCallback((receiver_id, content) => {
        if (content.length > 2000) {
            addToast("Message content exceeds 2000 character limit.", 'error');
            return;
        }

        const messagePayload = {
            type: 'message',
            payload: { receiver_id, content }
        };

        if (isConnected && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(messagePayload));
        } else {
            setMessageQueue(prev => [...prev, messagePayload]);
            addToast("Sending failed. Message queued for delivery on reconnect.", 'warning');
        }
    }, [isConnected, addToast]);

    return (
        <WSContext.Provider value={{ isConnected, messages, sendMessage, messageQueue }}>
            {children}
        </WSContext.Provider>
    );
};

const RouterContext = createContext();

const RouterProvider = ({ children }) => {
    const [currentPath, setCurrentPath] = useState(window.location.pathname);

    useEffect(() => {
        const handlePopState = () => setCurrentPath(window.location.pathname);
        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, []);

    const navigate = useCallback((path) => {
        window.history.pushState({}, '', path);
        setCurrentPath(path);
    }, []);

    return (
        <RouterContext.Provider value={{ currentPath, navigate }}>
            {children}
        </RouterContext.Provider>
    );
};

const FaircruitLogo = () => (
    <div className="logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
            <path d="M12 2L2 22H22L12 2ZM12 18L10 14H14L12 18Z" fill="#77A8A8"/>
            <path d="M12 14L14 10H10L12 14Z" fill="#77A8A8"/>
        </svg>
        <span style={{ color: '#222', fontWeight: 700 }}>Fair</span>
        <span style={{ color: '#77A8A8', fontWeight: 700 }}>cruit</span>
    </div>
);

const Header = () => {
    const { isLoggedIn, logout } = useAuth();
    const { navigate, currentPath } = useContext(RouterContext);

    const navTo = (path) => () => navigate(path);

    return (
        <header className="header">
            <div className="container header-content">
                <a onClick={navTo('/')} href="#" style={{ textDecoration: 'none' }}>
                    <FaircruitLogo />
                </a>
                <nav className="nav">
                    <a onClick={navTo('/')} href="#">Home</a>
                    <a onClick={navTo('/about')} href="#">About Us</a>
                    {isLoggedIn ? (
                        <button className="btn" onClick={logout} style={{ marginLeft: '16px' }}>Logout</button>
                    ) : (
                        <a className="btn" onClick={navTo('/get-started')} href="#">Get Started</a>
                    )}
                </nav>
            </div>
        </header>
    );
};

const Footer = () => (
    <footer className="footer">
        <div className="container footer-content">
            <div>
                <h3>faircruit</h3>
                <p>Hire by Competence, Not Credentials.</p>
            </div>
            <div>
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="#" style={{ color: 'var(--white)' }}>Careers</a></li>
                    <li><a href="#" style={{ color: 'var(--white)' }}>Ethics Policy</a></li>
                    <li><a href="#" style={{ color: 'var(--white)' }}>Terms of Service</a></li>
                </ul>
            </div>
            <div>
                <h3>Stay Updated</h3>
                <p style={{ marginBottom: '16px' }}>Sign up for our newsletter:</p>
                <form className="newsletter-form" onSubmit={(e) => { e.preventDefault(); alert('Newsletter sign-up simulated!'); }}>
                    <input type="email" placeholder="Your Email" aria-label="Newsletter Email" required />
                    <button type="submit" className="btn">Subscribe</button>
                </form>
            </div>
        </div>
        <div className="container" style={{ textAlign: 'center', marginTop: '32px', fontSize: '0.8rem', color: '#aaa' }}>
            <p>&copy; {new Date().getFullYear()} faircruit. All rights reserved.</p>
        </div>
    </footer>
);

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, authAxios } = useAuth();
    const { navigate } = useContext(RouterContext);
    const addToast = useToast();

    const loginMutation = useMutation({
        mutationFn: async ({ email, password }) => {
            const response = await authAxios.post('/auth/login', { email, password });
            return response.data;
        },
        onSuccess: (data) => {
            login(data.access_token, { id: data.user.id, role: data.user.role, username: data.user.username, email: data.user.email });
            addToast('Login successful!', 'success');
            navigate(`/dashboard/${data.user.role}`);
           
        },
        onError: (error) => {
            const status = error.response?.status;
            if (status === 429) {
                addToast("Rate limit exceeded (5/min). Try again in 60s.", 'error');
            } else if (status === 401) {
                addToast("Invalid email or password.", 'error');
            } else {
                addToast("An unexpected error occurred during login.", 'error');
            }
        }
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        loginMutation.mutate({ email, password });
    };

    return (
        <div className="form-container">
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="login-email">Email</label>
                    <input id="login-email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="login-password">Password</label>
                    <input id="login-password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className="btn" style={{ width: '100%' }} disabled={loginMutation.isPending}>
                    {loginMutation.isPending ? 'Logging In...' : 'Login'}
                </button>
                <p style={{ marginTop: '16px', textAlign: 'center', fontSize: '0.9rem' }}>
                    Need an account? <a href="#" onClick={() => navigate('/register')}>Register Here</a>
                </p>
            </form>
        </div>
    );
};

const RegisterForm = () => {
    const [form, setForm] = useState({ email: '', username: '', password: '', role: 'applicant' });
    const [errors, setErrors] = useState({});
    const { login, authAxios } = useAuth();
    const { navigate } = useContext(RouterContext);
    const addToast = useToast();

    const registerMutation = useMutation({
        mutationFn: async (data) => {
            const response = await authAxios.post('/auth/register', data);
            return response.data;
        },
        onSuccess: (data) => {
            login(data.access_token, { id: data.user.id, role: data.user.role, username: data.user.username, email: data.user.email });
            addToast('Registration successful!', 'success');
            navigate(`/dashboard/${data.user.role}`);
        },
        onError: (error) => {
            const status = error.response?.status;
            if (status === 409) {
                addToast(`Registration failed: ${error.response.data.detail}`, 'error');
            } else {
                addToast("An unexpected error occurred during registration.", 'error');
            }
        }
    });

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        if (form.password.length < 8) {
            setErrors({ password: "Password must be at least 8 characters." });
            addToast("Validation failed: Password too short.", 'error');
            return;
        }
        registerMutation.mutate(form);
    };

    return (
        <div className="form-container">
            <h2>Register</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="reg-username">Username</label>
                    <input id="reg-username" type="text" name="username" value={form.username} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label htmlFor="reg-email">Email</label>
                    <input id="reg-email" type="email" name="email" value={form.email} onChange={handleChange} required />
                </div>
                <div className="form-group">
                    <label htmlFor="reg-password">Password</label>
                    <input id="reg-password" type="password" name="password" value={form.password} onChange={handleChange} required />
                    {errors.password && <p className="error-message">{errors.password}</p>}
                </div>
                <div className="form-group">
                    <label htmlFor="reg-role">Role</label>
                    <select id="reg-role" name="role" value={form.role} onChange={handleChange} required>
                        <option value="applicant">Applicant</option>
                        <option value="recruiter">Recruiter</option>
                        <option value="admin">Admin (Request Only)</option>
                    </select>
                </div>
                <button type="submit" className="btn" style={{ width: '100%' }} disabled={registerMutation.isPending}>
                    {registerMutation.isPending ? 'Registering...' : 'Register'}
                </button>
            </form>
        </div>
    );
};

const MessagingUI = ({ otherUserId = 'admin-support-id' }) => {
    const { user, isRecruiter, isApplicant } = useAuth();
    const { isConnected, messages, sendMessage, messageQueue } = useWS();
    const [content, setContent] = useState('');
    const addToast = useToast();
    const messagesEndRef = useRef(null);

    const { data: history, isLoading: historyLoading } = useQuery({
        queryKey: ['messages', otherUserId],
        queryFn: async () => {
            const response = await authAxios.get(`/messages/${otherUserId}`);
            return response.data.map(msg => ({
                id: msg._id,
                sender_id: msg.sender_id,
                content: msg.content,
                timestamp: new Date(msg.timestamp).getTime()
            }));
        },
        enabled: !!otherUserId
    });

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, history]);

    const isSendDisabled = !isConnected || content.length === 0;

    const handleSubmit = (e) => {
        e.preventDefault();
        if (isSendDisabled) {
            addToast("Cannot send: Not connected or message is empty.", 'warning');
            return;
        }
        sendMessage(otherUserId, content);
        setContent('');
    };

    if (historyLoading) return <div>Loading messages...</div>;

    const displayMessages = [...(history || []), ...messages].sort((a, b) => a.timestamp - b.timestamp);

    return (
        <div className="message-container">
            <h3 style={{ padding: '16px', borderBottom: '1px solid #eee' }}>
                Chat with {isRecruiter ? 'Applicant' : 'Admin'} ({isConnected ? 'Online' : 'Offline - Queuing: ' + messageQueue.length})
            </h3>
            <div className="message-list">
                {displayMessages.map(msg => (
                    <div
                        key={msg.id}
                        className={`message-bubble ${msg.sender_id === user.id ? 'message-me' : 'message-them'}`}
                    >
                        {msg.content}
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <form className="message-input-area" onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Type your message (max 2000 chars)"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    maxLength={2000}
                    disabled={!isConnected}
                    aria-label="Message Input"
                />
                <button type="submit" className="btn" disabled={isSendDisabled}>Send</button>
            </form>
        </div>
    );
};

const UploadComponent = () => {
    const { authAxios } = useAuth();
    const addToast = useToast();
    const [file, setFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const abortControllerRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        if (selectedFile.size > VITE_MAX_UPLOAD_SIZE_BYTES) {
            addToast(`File size exceeds limit of ${VITE_MAX_UPLOAD_SIZE_BYTES / 1024 / 1024}MB.`, 'error');
            setFile(null);
            return;
        }

        if (!ALLOWED_MIMES_ARRAY.includes(selectedFile.type)) {
            addToast(`Unsupported file type: ${selectedFile.type}. Allowed: ${VITE_ALLOWED_UPLOAD_MIMES}`, 'error');
            setFile(null);
            return;
        }

        setFile(selectedFile);
        setUploadProgress(0);
    };

    const handleUpload = async () => {
        if (!file) {
            addToast("Please select a file first.", 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setIsUploading(true);
        abortControllerRef.current = new AbortController();

        try {
            const response = await authAxios.post('/applicant/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (progressEvent) => {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(percent);
                },
                signal: abortControllerRef.current.signal
            });

            addToast(`Upload successful: ${response.data.filename}`, 'success');
            setFile(null);
            setUploadProgress(100);
        } catch (error) {
            if (error.code === 'ERR_CANCELED') {
                addToast('Upload aborted by user.', 'info');
            } else if (error.response) {
                const status = error.response.status;
                if (status === 413) {
                    addToast("Upload failed: File size too large (413).", 'error');
                } else if (status === 415) {
                    addToast("Upload failed: Unsupported media type (415).", 'error');
                } else {
                    addToast(`Upload failed: ${error.response.data.detail || 'Server error'}`, 'error');
                }
            } else {
                addToast('Upload failed due to network error.', 'error');
            }
            setUploadProgress(0);
        } finally {
            setIsUploading(false);
        }
    };

    const handleAbort = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    return (
        <div className="card">
            <h3>Upload CV/Portfolio/Video</h3>
            <p>Supported formats: {VITE_ALLOWED_UPLOAD_MIMES}. Max size: {VITE_MAX_UPLOAD_SIZE_BYTES / 1024 / 1024} MB.</p>
            <input type="file" onChange={handleFileChange} accept={VITE_ALLOWED_UPLOAD_MIMES} style={{ marginTop: '16px' }} />
            {file && <p style={{ marginTop: '8px', fontStyle: 'italic' }}>Selected: {file.name} ({Math.round(file.size / 1024)} KB)</p>}

            <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                <button className="btn" onClick={handleUpload} disabled={!file || isUploading}>
                    {isUploading ? 'Uploading...' : 'Start Upload'}
                </button>
                {isUploading && (
                    <button className="btn" onClick={handleAbort} style={{ backgroundColor: '#cc3333' }}>
                        Abort
                    </button>
                )}
            </div>

            {isUploading && (
                <div className="progress-bar-container">
                    <div className="progress-bar" style={{ width: `${uploadProgress}%` }} aria-valuenow={uploadProgress} aria-valuemin="0" aria-valuemax="100" role="progressbar"></div>
                </div>
            )}
        </div>
    );
};

const JobEditor = ({ initialJob, onSubmit }) => {
    const [job, setJob] = useState(initialJob || { title: '', description: '', competencies: [{ level: 'Awareness', description: '', evidence_type: 'MCQ' }], evidence_types: ['pdf', 'video'], duration_minutes: 60, criteria: '' });
    const [errors, setErrors] = useState({});
    const addToast = useToast();

    const handleChange = (e) => setJob({ ...job, [e.target.name]: e.target.value });
    const handleCompetencyChange = (index, e) => {
        const newCompetencies = job.competencies.map((comp, i) => (
            i === index ? { ...comp, [e.target.name]: e.target.value } : comp
        ));
        setJob({ ...job, competencies: newCompetencies });
    };
    const addCompetency = () => setJob({ ...job, competencies: [...job.competencies, { level: 'Awareness', description: '', evidence_type: 'MCQ' }] });
    const removeCompetency = (index) => setJob({ ...job, competencies: job.competencies.filter((_, i) => i !== index) });

    const handleSubmit = (e) => {
        e.preventDefault();
        setErrors({});
        try {
            const validatedData = JobCreateSchema.parse({
                ...job,
                duration_minutes: Number(job.duration_minutes),
                evidence_types: Array.isArray(job.evidence_types) ? job.evidence_types : [job.evidence_types]
            });
            onSubmit(validatedData);
        } catch (error) {
            const validationErrors = error.flatten().fieldErrors;
            setErrors(validationErrors);
            addToast('Validation failed. Check the form for errors.', 'error');
        }
    };

    return (
        <form className="card" onSubmit={handleSubmit}>
            <h3>{initialJob ? 'Edit Job' : 'Create New Job'}</h3>
            <div className="form-group">
                <label htmlFor="job-title">Job Title</label>
                <input id="job-title" name="title" value={job.title} onChange={handleChange} required />
                {errors.title && <p className="error-message">{errors.title}</p>}
            </div>
            <div className="form-group">
                <label htmlFor="job-description">Description</label>
                <textarea id="job-description" name="description" value={job.description} onChange={handleChange} rows="4" required />
                {errors.description && <p className="error-message">{errors.description}</p>}
            </div>
            <div className="form-group">
                <label htmlFor="job-duration">Duration (Minutes)</label>
                <input id="job-duration" type="number" name="duration_minutes" value={job.duration_minutes} onChange={handleChange} min="10" required />
                {errors.duration_minutes && <p className="error-message">{errors.duration_minutes}</p>}
            </div>
            <div className="form-group">
                <label htmlFor="job-criteria">ML Criteria (Prompt)</label>
                <textarea id="job-criteria" name="criteria" value={job.criteria} onChange={handleChange} rows="3" required placeholder="Define the criteria for LLM analysis." />
                {errors.criteria && <p className="error-message">{errors.criteria}</p>}
            </div>
            <h4 style={{ marginTop: '24px', marginBottom: '16px', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Competencies</h4>
            {job.competencies.map((comp, index) => (
                <div key={index} style={{ border: '1px solid #ccc', padding: '16px', marginBottom: '16px', borderRadius: '4px' }}>
                    <h5 style={{ marginBottom: '8px', color: 'var(--primary)' }}>Competency #{index + 1}</h5>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr 50px', gap: '8px' }}>
                        <select name="level" value={comp.level} onChange={(e) => handleCompetencyChange(index, e)}>
                            {['Awareness', 'Application', 'Mastery', 'Influence'].map(l => <option key={l} value={l}>{l}</option>)}
                        </select>
                        <input name="description" placeholder="Description" value={comp.description} onChange={(e) => handleCompetencyChange(index, e)} required />
                        <input name="evidence_type" placeholder="Evidence Type" value={comp.evidence_type} onChange={(e) => handleCompetencyChange(index, e)} required />
                        <button type="button" className="btn" onClick={() => removeCompetency(index)} style={{ backgroundColor: '#cc3333', padding: '8px' }}>X</button>
                    </div>
                    {errors.competencies?.[index] && <p className="error-message">{errors.competencies[index]}</p>}
                </div>
            ))}
            <button type="button" className="btn" onClick={addCompetency} style={{ width: '100%', marginBottom: '24px' }}>Add Competency</button>
            <button type="submit" className="btn" style={{ width: '100%' }}>{initialJob ? 'Update Job' : 'Create Job'}</button>
        </form>
    );
};

const TestFlow = () => {
    // ──────────────────────────────────────────────────────────────
    // Hooks & state
    // ──────────────────────────────────────────────────────────────
    const { navigate } = useContext(RouterContext);
    const addToast = useToast();
    const [level, setLevel] = useState(1);
    const [timer, setTimer] = useState(1800);               // 30 min
    const [antiCheatCount, setAntiCheatCount] = useState(0);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [answer, setAnswer] = useState('');
    const [selectedOption, setSelectedOption] = useState(null);
    const [webcamActive, setWebcamActive] = useState(false);
    const maxAntiCheat = 3;
    const { authAxios } = useAuth();
    const videoRef = useRef(null);

    // ──────────────────────────────────────────────────────────────
    // Randomised MCQ pool (Level 1)
    // ──────────────────────────────────────────────────────────────
    const mcqs = [
        { q: "What is the primary difference between a hash map and a hash set?", options: ["Hash map allows duplicates", "Hash set stores key-value pairs", "Hash map stores only keys", "Hash set is ordered"], correct: 2 },
        { q: "Which data structure uses LIFO?", options: ["Queue", "Stack", "Heap", "Tree"], correct: 1 },
        { q: "What is the time complexity of binary search?", options: ["O(1)", "O(n)", "O(log n)", "O(n²)"], correct: 2 }
    ];
    const [currentMCQ] = useState(() => mcqs[Math.floor(Math.random() * mcqs.length)]);

    // ──────────────────────────────────────────────────────────────
    // Mutation – submit test
    // ──────────────────────────────────────────────────────────────
    const submitTestMutation = useMutation({
        mutationFn: async (payload) => {
            const response = await authAxios.post('/applicant/applications/j1/submit', payload);
            return response.data;
        },
        onSuccess: () => {
            addToast('Test submitted successfully!', 'success');
            navigate('/dashboard/applicant/results');
        },
        onError: () => {
            addToast('Submission failed. Try again.', 'error');
        }
    });

    // ──────────────────────────────────────────────────────────────
    // Full-screen enforcement
    // ──────────────────────────────────────────────────────────────
    useEffect(() => {
        const enterFullScreen = () => {
            const el = document.documentElement;
            if (el.requestFullscreen) el.requestFullscreen();
            else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
            else if (el.msRequestFullscreen) el.msRequestFullscreen();
        };
        enterFullScreen();

        const onFSChange = () => {
            const inFS = !!(
                document.fullscreenElement ||
                document.webkitFullscreenElement ||
                document.msFullscreenElement
            );
            setIsFullScreen(inFS);
            if (!inFS && level <= 3) {
                setAntiCheatCount(c => c + 1);
                addToast('FULLSCREEN EXITED – re-enter now.', 'error');
            }
        };
        document.addEventListener('fullscreenchange', onFSChange);
        return () => document.removeEventListener('fullscreenchange', onFSChange);
    }, [level, addToast]);

    // ──────────────────────────────────────────────────────────────
    // Tab-switch / visibility cheat detection
    // ──────────────────────────────────────────────────────────────
    useEffect(() => {
        const onVisibility = () => {
            if (document.hidden && level <= 3) {
                setAntiCheatCount(c => {
                    const newC = c + 1;
                    addToast(`TAB SWITCH DETECTED! Count: ${newC}/${maxAntiCheat}`, 'error');
                    if (newC >= maxAntiCheat) {
                        submitTestMutation.mutate({ level, content: answer, cheated: true });
                    }
                    return newC;
                });
            }
        };
        document.addEventListener('visibilitychange', onVisibility);
        return () => document.removeEventListener('visibilitychange', onVisibility);
    }, [level, answer, submitTestMutation, addToast]);

    // ──────────────────────────────────────────────────────────────
    // Copy / Paste / Right-click / shortcuts lockdown (levels 1-3)
    // ──────────────────────────────────────────────────────────────
    useEffect(() => {
        const block = (e) => {
            e.preventDefault();
            addToast('EXAM PROTECTION: Action disabled.', 'error');
            setAntiCheatCount(c => c + 1);
        };
        const blockShortcuts = (e) => {
            if (
                e.ctrlKey || e.metaKey || e.shiftKey ||
                ['F12', 'PrintScreen', 'ContextMenu'].includes(e.key)
            ) {
                e.preventDefault();
                addToast('EXAM PROTECTION: Shortcut blocked.', 'error');
                setAntiCheatCount(c => c + 1);
            }
        };

        if (level <= 3) {
            document.addEventListener('copy', block);
            document.addEventListener('paste', block);
            document.addEventListener('cut', block);
            document.addEventListener('contextmenu', block);
            document.addEventListener('selectstart', block);
            document.addEventListener('dragstart', block);
            document.addEventListener('keydown', blockShortcuts);
        }

        return () => {
            document.removeEventListener('copy', block);
            document.removeEventListener('paste', block);
            document.removeEventListener('cut', block);
            document.removeEventListener('contextmenu', block);
            document.removeEventListener('selectstart', block);
            document.removeEventListener('dragstart', block);
            document.removeEventListener('keydown', blockShortcuts);
        };
    }, [level, addToast]);

    // ──────────────────────────────────────────────────────────────
    // Webcam (Level 4)
    // ──────────────────────────────────────────────────────────────
    useEffect(() => {
        if (level === 4) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                        setWebcamActive(true);
                    }
                })
                .catch(() => addToast('WEBCAM REQUIRED – allow access to continue.', 'error'));
        }
        return () => {
            if (videoRef.current?.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(t => t.stop());
            }
        };
    }, [level, addToast]);

    // ──────────────────────────────────────────────────────────────
    // Timer
    // ──────────────────────────────────────────────────────────────
    useEffect(() => {
        const id = setInterval(() => {
            setTimer(t => {
                if (t <= 1) {
                    clearInterval(id);
                    addToast('TIME EXPIRED – auto-submitting…', 'error');
                    submitTestMutation.mutate({ level, content: answer });
                    return 0;
                }
                return t - 1;
            });
        }, 1000);
        return () => clearInterval(id);
    }, [level, answer, submitTestMutation, addToast]);

    // ──────────────────────────────────────────────────────────────
    // Helpers
    // ──────────────────────────────────────────────────────────────
    const formatTime = (s) => {
        const m = Math.floor(s / 60).toString().padStart(2, '0');
        const sec = (s % 60).toString().padStart(2, '0');
        return `${m}:${sec}`;
    };

    const nextLevel = () => {
        if (level < 4) {
            setLevel(level + 1);
            setTimer(1800);
            setAnswer('');
            setSelectedOption(null);
            addToast(`Level ${level + 1} started.`, 'info');
        } else {
            const payload = level === 1
                ? { level, mcq_answer: selectedOption, correct: selectedOption === currentMCQ.correct }
                : { level, content: answer };
            submitTestMutation.mutate(payload);
        }
    };

    // ──────────────────────────────────────────────────────────────
    // Render
    // ──────────────────────────────────────────────────────────────
    return (
        <div className="test-flow-container" style={{ padding: '32px', fontFamily: 'Roboto, sans-serif' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div className="test-timer" style={{ fontWeight: 'bold', fontSize: '1.3rem', color: '#cc3333' }}>
                    Time: {formatTime(timer)}
                </div>
                {!isFullScreen && <div style={{ color: '#cc3333', fontWeight: 'bold' }}>FULLSCREEN REQUIRED</div>}
            </div>

            {/* Anti-cheat warning */}
            {antiCheatCount > 0 && antiCheatCount < maxAntiCheat && (
                <div style={{
                    background: '#ffebee',
                    padding: '12px',
                    borderRadius: '6px',
                    marginBottom: '16px',
                    color: '#c62828'
                }}>
                    <strong>WARNING:</strong> {antiCheatCount}/{maxAntiCheat} violations – next = auto-submit.
                </div>
            )}

            <div className="card" style={{
                background: '#fff',
                padding: '24px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
                <h2 style={{ color: '#77A8A8', marginBottom: '8px' }}>
                    Level {level}: {['Awareness (MCQ)', 'Application (Coding)', 'Mastery (Essay)', 'Influence (Video)'][level - 1]}
                </h2>
                <p style={{
                    fontStyle: 'italic',
                    color: level <= 3 ? '#cc3333' : '#666',
                    marginBottom: '16px'
                }}>
                    {level <= 3
                        ? 'Copy/Paste/Right-Click/Tab-Switch disabled.'
                        : 'Record your 2-minute response.'}
                </p>

                {/* ---------- LEVEL 1 – MCQ ---------- */}
                {level === 1 && (
                    <div>
                        <p><strong>Q:</strong> {currentMCQ.q}</p>
                        {currentMCQ.options.map((opt, i) => (
                            <label key={i} style={{ display: 'block', margin: '10px 0' }}>
                                <input
                                    type="radio"
                                    name="mcq"
                                    checked={selectedOption === i}
                                    onChange={() => setSelectedOption(i)}
                                    style={{ marginRight: '8px' }}
                                />
                                {opt}
                            </label>
                        ))}
                    </div>
                )}

                {/* ---------- LEVEL 2 & 3 – Text ---------- */}
                {(level === 2 || level === 3) && (
                    <>
                        {level === 2 && <p><strong>Task:</strong> Write a recursive Fibonacci function.</p>}
                        {level === 3 && <p><strong>Essay:</strong> Describe technical leadership.</p>}
                        <textarea
                            rows="10"
                            placeholder="Your answer here..."
                            value={answer}
                            onChange={e => setAnswer(e.target.value)}
                            style={{
                                width: '100%',
                                marginTop: '16px',
                                padding: '12px',
                                fontSize: '1rem',
                                border: '1px solid #ccc',
                                borderRadius: '4px'
                            }}
                        />
                    </>
                )}

                {/* ---------- LEVEL 4 – Video ---------- */}
                {level === 4 && (
                    <div>
                        <p><strong>Prompt:</strong> Explain a system outage solution in 2 minutes.</p>
                        {webcamActive ? (
                            <video
                                ref={videoRef}
                                autoPlay
                                muted
                                style={{
                                    width: '100%',
                                    maxHeight: '300px',
                                    border: '2px solid #77A8A8',
                                    borderRadius: '8px',
                                    marginTop: '16px'
                                }}
                            />
                        ) : (
                            <p style={{ color: '#cc3333', fontWeight: 'bold' }}>Webcam access required.</p>
                        )}
                    </div>
                )}

                {/* Progress & Submit */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
                    <p style={{ fontWeight: 'bold' }}>Progress: Level {level}/4</p>
                    <button
                        className="btn"
                        onClick={nextLevel}
                        disabled={
                            (level === 1 && selectedOption === null) ||
                            (level !== 1 && level !== 4 && !answer.trim()) ||
                            (level === 4 && !webcamActive)
                        }
                        style={{
                            background: '#77A8A8',
                            color: 'white',
                            padding: '10px 20px',
                            border: 'none',
                            borderRadius: '6px',
                            fontWeight: 'bold',
                            cursor: 'pointer'
                        }}
                    >
                        {level < 4 ? 'Submit & Next' : 'Finish & Submit'}
                    </button>
                </div>
            </div>

            {/* Full-screen button */}
            <button
                onClick={() => document.documentElement.requestFullscreen?.()}
                style={{
                    marginTop: '16px',
                    padding: '10px 20px',
                    background: isFullScreen ? '#77A8A8' : '#cc3333',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 'bold'
                }}
            >
                {isFullScreen ? 'In Full Screen' : 'Enter Full Screen (Required)'}
            </button>
        </div>
    );
};

const ApplicantDashboard = () => {
    const { navigate } = useContext(RouterContext);
    const { user, authAxios } = useAuth();
    const [view, setView] = useState('home');

    const { data: jobs, isLoading: jobsLoading } = useQuery({
        queryKey: ['jobs'],
        queryFn: async () => {
            const response = await authAxios.get('/applicant/applications');
            return response.data.items;
        }
    });

    const ApplicantHome = () => {
        if (jobsLoading) return <div>Loading jobs...</div>;

        return (
            <>
                <h2 style={{ marginBottom: '32px' }}>Welcome, {user.username}!</h2>
                <UploadComponent />
                <div className="card">
                    <h3>Job Selection Grid</h3>
                    <div className="grid-3">
                        {jobs.map(job => (
                            <div key={job.id} style={{ padding: '16px', border: '1px solid #ccc', borderRadius: '8px' }}>
                                <h4>{job.title}</h4>
                                <p>Status: {job.status}</p>
                                {job.test_ready ? (
                                    <button className="btn" onClick={() => navigate('/dashboard/applicant/test')} style={{ marginTop: '16px' }}>Start Test</button>
                                ) : (
                                    <button className="btn" disabled style={{ marginTop: '16px', backgroundColor: '#aaa' }}>Awaiting Eligibility</button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </>
        );
    };

    const ApplicantResults = () => {
        const { data: results, isLoading: resultsLoading } = useQuery({
            queryKey: ['results'],
            queryFn: async () => {
                const response = await authAxios.get('/applicant/results');
                return response.data;
            }
        });

        if (resultsLoading) return <div>Loading results...</div>;

        const RadarChart = ({ scores }) => {
            const size = 200;
            const center = size / 2;
            const max = 100;
            const points = scores.length;
            const angleStep = (2 * Math.PI) / points;

            const getCoord = (value, index) => {
                const radius = (value / max) * center;
                const angle = index * angleStep - Math.PI / 2;
                const x = center + radius * Math.cos(angle);
                const y = center + radius * Math.sin(angle);
                return `${x},${y}`;
            };

            const pointString = scores.map((s, i) => getCoord(s.score, i)).join(' ');

            return (
                <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                    {[1, 2, 3, 4].map(i => (
                        <polygon key={i} points={scores.map((s, idx) => getCoord(max * (i * 0.25), idx)).join(' ')} fill="none" stroke="#ccc" strokeDasharray="2 2" />
                    ))}
                    <polygon points={pointString} fill="rgba(119, 168, 168, 0.4)" stroke="var(--primary-dark)" strokeWidth="2" />
                    {scores.map((s, i) => (
                        <text key={i} x={center + center * Math.cos(i * angleStep - Math.PI / 2) * 1.1} y={center + center * Math.sin(i * angleStep - Math.PI / 2) * 1.1} fontSize="10" textAnchor="middle">
                            {s.name} ({s.score}%)
                        </text>
                    ))}
                </svg>
            );
        };

        const handleExportPDF = () => {
            alert('Simulated PDF Export of the Applicant Report.');
        };

        return (
            <div className="card">
                <h2>Evaluation Results for {user.username}</h2>
                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary-dark)' }}>Overall Competency Score: {results.score}%</p>
                <div style={{ display: 'flex', gap: '40px', alignItems: 'center', marginTop: '32px' }}>
                    <div style={{ flexShrink: 0 }}>
                        <RadarChart scores={results.competencies} />
                    </div>
                    <div>
                        <h3>Report Summary</h3>
                        <p><strong>Strengths:</strong> {results.strengths}</p>
                        <p><strong>Weaknesses:</strong> {results.weaknesses}</p>
                        <p><strong>Recommendations:</strong> {results.recommendations}</p>
                    </div>
                </div>
                <button className="btn" onClick={handleExportPDF} style={{ marginTop: '32px' }}>
                    Export Full Report PDF
                </button>
            </div>
        );
    };

    const componentMap = {
        home: <ApplicantHome />,
        applications: <div className="card"><h3>My Applications</h3><p>Detailed list of all applications and their stages.</p></div>,
        tests: <div className="card"><h3>My Tests</h3><p>Active and past test records.</p></div>,
        results: <ApplicantResults />,
        profile: <div className="card"><h3>Profile Settings</h3><p>Manage your personal data.</p></div>,
        messages: <MessagingUI otherUserId="recruiter-r2"/>
    };

    return (
        <div className="dashboard-layout">
            <div className="sidebar">
                <nav>
                    {Object.keys(componentMap).map(key => (
                        <a key={key} href="#" className={view === key ? 'active' : ''} onClick={() => setView(key)}>
                            {key.charAt(0).toUpperCase() + key.slice(1)}
                        </a>
                    ))}
                    <a href="#" onClick={() => { alert('Profile logout simulated'); navigate('/login')}}>Logout</a>
                </nav>
            </div>
            <div className="main-content">
                {componentMap[view]}
            </div>
        </div>
    );
};

const RecruiterDashboard = () => {
    const { authAxios } = useAuth();
    const addToast = useToast();
    const [view, setView] = useState('jobs');
    const [editingJob, setEditingJob] = useState(null);

    const { data: jobs, isLoading: jobsLoading } = useQuery({
        queryKey: ['recruiter_jobs'],
        queryFn: async () => {
            const response = await authAxios.get('/recruiter/jobs');
            return response.data;
        }
    });

    const createJobMutation = useMutation({
        mutationFn: async (data) => {
            const response = await authAxios.post('/recruiter/jobs', data);
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries(['recruiter_jobs']);
            addToast(`Job "${data.title}" created!`, 'success');
            setEditingJob(null);
            setView('jobs');
        },
        onError: (error) => {
            addToast(`Job creation failed: ${error.response?.data?.detail || 'Server error'}`, 'error');
        }
    });

    const updateJobMutation = useMutation({
        mutationFn: async (data) => {
            const response = await authAxios.put(`/recruiter/jobs/${data.id}`, data);
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries(['recruiter_jobs']);
            addToast(`Job "${data.title}" updated!`, 'success');
            setEditingJob(null);
            setView('jobs');
        },
        onError: (error) => {
            addToast(`Job update failed: ${error.response?.data?.detail || 'Server error'}`, 'error');
        }
    });

    const deleteJobMutation = useMutation({
        mutationFn: async (id) => {
            await authAxios.delete(`/recruiter/jobs/${id}`);
            return { id };
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['recruiter_jobs']);
            addToast('Job deleted!', 'success');
        },
        onError: (error) => {
            addToast(`Job deletion failed: ${error.response?.data?.detail || 'Server error'}`, 'error');
        }
    });

    const handleJobSubmit = async (jobData) => {
        if (jobData.id) {
            updateJobMutation.mutate(jobData);
        } else {
            createJobMutation.mutate(jobData);
        }
    };

    const JobManagement = () => {
        if (jobsLoading) return <div>Loading jobs...</div>;

        return (
            <>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                    <h2>Job Postings</h2>
                    <button className="btn" onClick={() => setEditingJob({})}>+ Post New Job</button>
                </div>
                <div className="grid-3">
                    {jobs.map(job => (
                        <div key={job.id} className="card" style={{ padding: '16px' }}>
                            <h4>{job.title}</h4>
                            <p style={{ color: 'var(--text-light)', fontSize: '0.9rem' }}>{job.competencies.length} competencies defined.</p>
                            <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
                                <button className="btn" style={{ padding: '8px 16px' }} onClick={() => setEditingJob(job)}>Edit</button>
                                <button className="btn" style={{ backgroundColor: '#cc3333', padding: '8px 16px' }} onClick={() => { if (window.confirm('Are you sure?')) deleteJobMutation.mutate(job.id); }}>Delete</button>
                            </div>
                        </div>
                    ))}
                </div>
            </>
        );
    };

    const ApplicantReview = () => {
        const { data: applicants, isLoading: applicantsLoading } = useQuery({
            queryKey: ['applicants'],
            queryFn: async () => {
                const response = await authAxios.get('/recruiter/applicants');
                return response.data;
            }
        });

        if (applicantsLoading) return <div>Loading applicants...</div>;

        return (
            <div className="card">
                <h2>Applicant List</h2>
                <ul style={{ listStyle: 'none' }}>
                    {applicants.map(app => (
                        <li key={app.id} style={{ borderBottom: '1px solid #eee', padding: '12px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>{app.name} - Score: {app.score}%</span>
                            {app.report_ready ? (
                                <button className="btn" style={{ padding: '8px 16px' }} onClick={() => alert(`Viewing ML Report for ${app.name}`)}>View ML Report</button>
                            ) : (
                                <span style={{ color: 'var(--text-light)' }}>Report in Progress...</span>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    const componentMap = {
        jobs: editingJob ? <JobEditor initialJob={editingJob} onSubmit={handleJobSubmit} /> : <JobManagement />,
        applicants: <ApplicantReview />,
        messages: <MessagingUI otherUserId="admin-a1" />
    };

    return (
        <div className="dashboard-layout">
            <div className="sidebar">
                <nav>
                    {Object.keys(componentMap).map(key => (
                        <a key={key} href="#" className={view === key ? 'active' : ''} onClick={() => { setView(key); setEditingJob(null); }}>
                            {key.charAt(0).toUpperCase() + key.slice(1)}
                        </a>
                    ))}
                </nav>
            </div>
            <div className="main-content">
                {componentMap[view]}
            </div>
        </div>
    );
};

const AdminDashboard = () => {
    const { isAdmin, authAxios } = useAuth();
    const { navigate } = useContext(RouterContext);
    const [view, setView] = useState('analytics');

    if (!isAdmin) {
        return <div className="card"><h1>Access Denied</h1><p>You must be an Administrator to view this page.</p></div>;
    }

    const Analytics = () => (
        <div className="card">
            <h2>Competency Breakdown Analytics</h2>
            <div className="grid-3">
                <div className="analytics-chart">
                    <h3>Overall Score Distribution</h3>
                    <p style={{ height: '150px', lineHeight: '150px' }}>[Placeholder for Bar/Histogram Chart]</p>
                </div>
                <div className="analytics-chart">
                    <h3>Average Score by Role</h3>
                    <p style={{ height: '150px', lineHeight: '150px' }}>[Placeholder for Bar Chart]</p>
                </div>
                <div className="analytics-chart">
                    <h3>Bias Metrics (Redacted vs. Full)</h3>
                    <p style={{ height: '150px', lineHeight: '150px' }}>[Placeholder for Scatter Plot]</p>
                </div>
            </div>
        </div>
    );

    const AuditLogs = () => {
        const { data: logs, isLoading: logsLoading } = useQuery({
            queryKey: ['audit_logs'],
            queryFn: async () => {
                const response = await authAxios.get('/admin/audit-logs?page=1&size=20');
                return response.data;
            }
        });

        if (logsLoading) return <div>Loading audit logs...</div>;

        return (
            <div className="card">
                <h2>Audit Logs</h2>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '16px' }}>
                    <thead>
                        <tr style={{ background: 'var(--primary-dark)', color: 'var(--white)' }}>
                            <th style={{ padding: '8px' }}>Timestamp</th>
                            <th style={{ padding: '8px' }}>User ID</th>
                            <th style={{ padding: '8px' }}>Action</th>
                            <th style={{ padding: '8px' }}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map(log => (
                            <tr key={log.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td>{new Date(log.timestamp).toLocaleString()}</td>
                                <td>{log.user_id}</td>
                                <td>{log.action}</td>
                                <td>{log.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const componentMap = {
        analytics: <Analytics />,
        auditlogs: <AuditLogs />,
        messages: <MessagingUI otherUserId="recruiter-r2"/>
    };

    return (
        <div className="dashboard-layout">
            <div className="sidebar">
                <nav>
                    {Object.keys(componentMap).map(key => (
                        <a key={key} href="#" className={view === key ? 'active' : ''} onClick={() => setView(key)}>
                            {key.split(/(?=[A-Z])/).join(' ').replace('logs', ' Logs')}
                        </a>
                    ))}
                </nav>
            </div>
            <div className="main-content">
                {componentMap[view]}
            </div>
        </div>
    );
};

const LandingPage = () => {
    const { navigate } = useContext(RouterContext);

    return (
        <>
            <div className="hero-section">
                <div className="container">
                    <h1>Hire by Competence, Not Credentials.</h1>
                    <p>A data-driven, bias-reduced platform using LLM analysis and a structured 4-level evaluation system.</p>
                    <div className="cta-group">
                        <button className="btn" onClick={() => navigate('/get-started')}>Start as Applicant</button>
                        <button className="btn" onClick={() => navigate('/get-started')}>Post a Job</button>
                    </div>
                </div>
            </div>
            <div className="container" style={{ paddingTop: '64px' }}>
                <h2>How It Works: Our Structured Process</h2>
                <div className="timeline">
                    <div className="timeline-step">
                        <div className="timeline-step-icon">1</div>
                        <h3>Upload & Assess</h3>
                        <p>Applicants submit evidence and complete 4-level competency tests.</p>
                    </div>
                    <div className="timeline-step">
                        <div className="timeline-step-icon">2</div>
                        <h3>AI Analyze & Map</h3>
                        <p>LLMs process evidence, map skills to rubrics, and generate a profile vector.</p>
                    </div>
                    <div className="timeline-step">
                        <div className="timeline-step-icon">3</div>
                        <h3>Recruit & Hire</h3>
                        <p>Recruiters review objective scores and in-depth ML reports for selection.</p>
                    </div>
                </div>
            </div>
            <div className="container" style={{ paddingTop: '64px', paddingBottom: '64px' }}>
                <h2>Key Features</h2>
                <div className="grid-3">
                    <div className="card feature-card">
                        <h3>4-Level System</h3>
                        <p>Evaluate talent across Awareness, Application, Mastery, and Influence.</p>
                    </div>
                    <div className="card feature-card">
                        <h3>LLM Analysis</h3>
                        <p>Leverage advanced AI to extract insights from text and code submissions.</p>
                    </div>
                    <div className="card feature-card">
                        <h3>Bias-Reduced Scoring</h3>
                        <p>Demographic redaction and blind scoring mitigate bias.</p>
                    </div>
                </div>
            </div>
            <Footer />
        </>
    );
};

const AboutUs = () => (
    <>
        <div className="container" style={{ padding: '64px 0', minHeight: '60vh' }}>
            <h1>About faircruit</h1>
            <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
                <p><strong>Goal:</strong> faircruit prioritizes verifiable skills over biased credentials.</p>
                <h3>How Applicants Participate</h3>
                <p>Applicants create profiles, select jobs, upload evidence, and complete a four-level test with exam protections.</p>
                <h3>Recruiter Responsibilities</h3>
                <p>Recruiters define jobs, set rubrics, and review AI-generated reports.</p>
                <h3>Admin Responsibilities</h3>
                <p>Admins monitor analytics, audit logs, and ensure platform fairness.</p>
                <h3>Security, Ethics, and Data</h3>
                <p>JWT authentication, proctored tests, redacted data, and GDPR-compliant handling ensure security and privacy.</p>
            </div>
        </div>
        <Footer />
    </>
);

const GetStarted = () => {
    const { navigate } = useContext(RouterContext);
    return (
        <div className="container" style={{ padding: '64px 0', minHeight: '60vh', textAlign: 'center' }}>
            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                <h1>Choose Your Role</h1>
                <p style={{ marginBottom: '32px' }}>Select how you intend to use faircruit.</p>
                <div className="cta-group">
                    <button className="btn" onClick={() => navigate('/login')}>I am an Applicant</button>
                    <button className="btn" onClick={() => navigate('/login')}>I am a Recruiter / Admin</button>
                </div>
            </div>
        </div>
    );
};

const NotFound = () => (
    <div className="container" style={{ padding: '64px 0', minHeight: '60vh', textAlign: 'center' }}>
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <button className="btn" onClick={() => navigate('/')}>Go Home</button>
    </div>
);

const ProtectedRoute = ({ children, allowedRoles }) => {
    const { isLoggedIn, user, logout } = useAuth();
    const { navigate } = useContext(RouterContext);
    const addToast = useToast();

    useEffect(() => {
        if (!isLoggedIn) {
            navigate('/login');
            addToast("You must log in to access this page.", 'error');
        } else if (allowedRoles && !allowedRoles.includes(user.role)) {
            logout();
            navigate('/login');
            addToast("Access denied for your role.", 'error');
        }
    }, [isLoggedIn, user, allowedRoles, navigate, addToast, logout]);

    return isLoggedIn && (!allowedRoles || allowedRoles.includes(user.role)) ? children : null;
};

const AppContent = () => {
    const { currentPath } = useContext(RouterContext);
    const { isLoggedIn, user } = useAuth();

    const getDashboardPath = () => {
        if (!user || !user.role) return '/login';
        return `/dashboard/${user.role}`;
    };

    let content;

    if (currentPath === '/') {
        content = <LandingPage />;
    } else if (currentPath === '/about') {
        content = <AboutUs />;
    } else if (currentPath === '/get-started') {
        content = <GetStarted />;
    } else if (currentPath === '/login') {
        content = isLoggedIn ? <ProtectedRoute><Redirect to={getDashboardPath()} /></ProtectedRoute> : <LoginForm />;
    } else if (currentPath === '/register') {
        content = <RegisterForm />;
    } else if (currentPath.startsWith('/dashboard/applicant/test')) {
        content = <ProtectedRoute allowedRoles={['applicant']}><TestFlow /></ProtectedRoute>;
    } else if (currentPath === '/dashboard/applicant' || currentPath === '/dashboard/applicant/results') {
        content = <ProtectedRoute allowedRoles={['applicant']}><ApplicantDashboard /></ProtectedRoute>;
    } else if (currentPath === '/dashboard/recruiter') {
        content = <ProtectedRoute allowedRoles={['recruiter']}><RecruiterDashboard /></ProtectedRoute>;
    } else if (currentPath === '/dashboard/admin' || currentPath === '/dashboard/admin/analytics' || currentPath === '/dashboard/admin/audit-logs') {
        content = <ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>;
    } else {
        content = <NotFound />;
    }

    const showHeader = !currentPath.startsWith('/dashboard') || currentPath === '/dashboard/applicant' || currentPath === '/dashboard/recruiter' || currentPath === '/dashboard/admin';

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            {showHeader && <Header />}
            <main style={{ flexGrow: 1 }}>
                {content}
            </main>
        </div>
    );
};

const Redirect = ({ to }) => {
    const { navigate } = useContext(RouterContext);
    useEffect(() => navigate(to), [to, navigate]);
    return null;
};


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

export default App;