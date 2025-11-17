// Backend.jsx
import React, { useState, useEffect, useContext, createContext, useCallback, useRef, useMemo } from 'react';
import { QueryClient, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { z as Zod } from 'zod';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
// navigation will be performed via window.location to avoid requiring Router context here

/* ──────────────────────── ENV & CONSTANTS ──────────────────────── */
const VITE_API_BASE = import.meta.env.VITE_API_BASE;
const VITE_WS_BASE = import.meta.env.VITE_WS_BASE;
const VITE_MAX_UPLOAD_SIZE_BYTES = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE_BYTES) || 5242880;
const VITE_ALLOWED_UPLOAD_MIMES = import.meta.env.VITE_ALLOWED_UPLOAD_MIMES || 'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,video/mp4';
const ALLOWED_MIMES_ARRAY = VITE_ALLOWED_UPLOAD_MIMES.split(',').map(m => m.trim());

/* ──────────────────────── QUERY CLIENT ──────────────────────── */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 2, staleTime: 5 * 60 * 1000, cacheTime: 30 * 60 * 1000 },
  },
});

/* ──────────────────────── AXIOS INSTANCE ──────────────────────── */
export const authAxios = axios.create({
  baseURL: VITE_API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

/* ──────────────────────── AUTH CONTEXT ──────────────────────── */
const AuthContext = createContext();
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const addToast = useToast();

  // REACTIVE AXIOS
  const authAxios = useMemo(() => {
    const instance = axios.create({
      baseURL: '/api/v1',
    });

    instance.interceptors.request.use(config => {
      const token = localStorage.getItem('token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    instance.interceptors.response.use(
      res => res,
      err => {
        if (err.response?.status === 401) {
          logout();
          try { window.location.href = '/login'; } catch (e) {}
          addToast('Session expired. Please login again.', 'error');
        }
        return Promise.reject(err);
      }
    );

    return instance;
  }, [navigate, addToast]);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsLoggedIn(false);
    try { window.location.href = '/login'; } catch (e) {}
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Validate token
      authAxios.get('/api/v1/auth/me')
        .then(res => {
          setUser(res.data);
          setIsLoggedIn(true);
        })
        .catch(() => {
          localStorage.removeItem('token');
        });
    }
  }, [authAxios]);

  return { user, isLoggedIn, login, logout, authAxios };
};
export const AuthProvider = ({ children, navigate, addToast }) => {
  const [token, setToken] = useState(() => localStorage.getItem('authToken'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem('authToken', token);
      authAxios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('authToken');
      delete authAxios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user));
    else localStorage.removeItem('user');
  }, [user]);

  const login = (jwt, data) => {
    setToken(jwt);
    setUser(data);
  };

  const logout = useCallback(() => {
    try {
      authAxios.post('/api/v1/auth/logout');
    } catch (_) {}
    setToken(null);
    setUser(null);
    localStorage.clear();
    queryClient.clear();
    navigate?.('/');
    addToast?.('Successfully logged out', 'success');
  }, [navigate, addToast]);

  const isLoggedIn = !!token && !!user;
  const isAdmin = isLoggedIn && user?.role === 'admin';
  const isRecruiter = isLoggedIn && user?.role === 'recruiter';
  const isApplicant = isLoggedIn && user?.role === 'applicant';

  return (
    <AuthContext.Provider value={{
      token, user, login, logout, isLoggedIn, isAdmin, isRecruiter, isApplicant, authAxios
    }}>
      {children}
    </AuthContext.Provider>
  );
};

/* ──────────────────────── TOAST PROVIDER ──────────────────────── */
const ToastContext = createContext();
export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const add = useCallback((msg, type = 'info', dur = 5000) => {
    const id = Date.now();
    setToasts(p => [...p, { id, msg, type }]);
    setTimeout(() => setToasts(p => p.filter(t => t.id !== id)), dur);
  }, []);
  return (
    <ToastContext.Provider value={add}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>{t.msg}</div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

/* ──────────────────────── WEBSOCKET PROVIDER ──────────────────────── */
const WebSocketContext = createContext(null);
export const useWebSocket = () => {
  const ctx = useContext(WebSocketContext);
  if (!ctx) throw new Error('useWebSocket must be inside WebSocketProvider');
  return ctx;
};

export const WebSocketProvider = ({ children }) => {
  const { user, token } = useAuth();
  const addToast = useToast();
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const backoffRef = useRef(1000);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [queue, setQueue] = useState([]);

  const connect = useCallback(() => {
    if (!user?.id || wsRef.current) return;

    const url = `${VITE_WS_BASE}/api/v1/ws/messages/${user.id}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'auth', token }));
      backoffRef.current = 1000;
    };

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'auth_ok') {
          setIsConnected(true);
          setQueue(q => {
            q.forEach(m => ws.send(JSON.stringify(m)));
            return [];
          });
        } else if (data.type === 'new_message') {
          setMessages(prev => [...prev, {
            id: data.payload._id,
            sender_id: data.payload.sender_id,
            content: data.payload.content,
            timestamp: new Date(data.payload.timestamp).getTime(),
          }]);
        }
      } catch (_) {}
    };

    ws.onclose = () => {
      wsRef.current = null;
      setIsConnected(false);
      if (user?.id) {
        const delay = backoffRef.current;
        backoffRef.current = Math.min(backoffRef.current * 2, 30000);
        reconnectRef.current = setTimeout(connect, delay);
        addToast?.(`Reconnecting in ${delay}ms`, 'warning');
      }
    };

    ws.onerror = () => ws.close();
  }, [user?.id, token, addToast]);

  useEffect(() => {
    if (user?.id) connect();
    return () => {
      wsRef.current?.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [user?.id, connect]);

  const sendMessage = useCallback((receiver_id, content) => {
    if (!content.trim()) return addToast?.('Empty message', 'warning');
    if (content.length > 2000) return addToast?.('Too long', 'error');
    const payload = { receiver_id, content };
    if (isConnected && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    } else {
      setQueue(q => [...q, payload]);
      addToast?.('Queued', 'info');
    }
  }, [isConnected, addToast]);

  return (
    <WebSocketContext.Provider value={{ isConnected, messages, sendMessage, messageQueue: queue }}>
      {children}
    </WebSocketContext.Provider>
  );
};

/* ──────────────────────── ZOD SCHEMAS ──────────────────────── */
export const CompetencySchema = Zod.object({
  level: Zod.string().nonempty('Level is required'),
  description: Zod.string().min(1, 'Description is required'),
  evidence_type: Zod.string().nonempty('Evidence type is required'),
});

export const JobCreateSchema = Zod.object({
  title: Zod.string().min(3, 'Title must be at least 3 characters'),
  description: Zod.string().min(10, 'Description must be at least 10 characters'),
  competencies: Zod.array(CompetencySchema).min(1, 'At least one competency required'),
  evidence_types: Zod.array(Zod.string().nonempty()).min(1, 'At least one evidence type required'),
  duration_minutes: Zod.number().min(10, 'Duration must be at least 10 minutes'),
  criteria: Zod.string().min(10, 'Criteria must be at least 10 characters'),
});

/* ──────────────────────── FILE UPLOAD HOOK ──────────────────────── */
export const useFileUpload = () => {
  const { authAxios } = useAuth();
  const toast = useToast();
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const controllerRef = useRef(null);

  const upload = async (file) => {
    if (file.size > VITE_MAX_UPLOAD_SIZE_BYTES) return toast(`File >${VITE_MAX_UPLOAD_SIZE_BYTES / 1024 / 1024}MB`, 'error');
    if (!ALLOWED_MIMES_ARRAY.includes(file.type)) return toast(`Invalid type: ${file.type}`, 'error');

    const form = new FormData();
    form.append('file', file);
    setUploading(true);
    controllerRef.current = new AbortController();

    try {
      await authAxios.post('/api/v1/applicant/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: e => setProgress(Math.round((e.loaded * 100) / e.total)),
        signal: controllerRef.current.signal,
      });
      toast('Upload success', 'success');
      setProgress(100);
    } catch (err) {
      if (err.code === 'ERR_CANCELED') toast('Aborted', 'info');
      else toast(err.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  const abort = () => controllerRef.current?.abort();

  return { upload, progress, uploading, abort };
};

/* ──────────────────────── JOB HOOKS ──────────────────────── */
export const useJobs = () => {
  const { authAxios } = useAuth();
  return useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await authAxios.get('/api/v1/jobs');
      return response.data.items || [];
    },
    staleTime: 5 * 60 * 1000,
  });
};

export const useRecruiterJobs = () => {
  const { authAxios } = useAuth();
  return useQuery({
    queryKey: ['recruiter_jobs'],
    queryFn: async () => (await authAxios.get('/api/v1/recruiter/jobs')).data,
  });
};

export const useCreateJob = () => {
  const { authAxios } = useAuth();
  const toast = useToast();
  return useMutation({
    mutationFn: (data) => authAxios.post('/api/v1/recruiter/jobs', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recruiter_jobs'] });
      toast('Job created', 'success');
    },
  });
};

export const useUpdateJob = () => {
  const { authAxios } = useAuth();
  const toast = useToast();
  return useMutation({
    mutationFn: ({ id, ...data }) => authAxios.put(`/api/v1/recruiter/jobs/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recruiter_jobs'] });
      toast('Job updated', 'success');
    },
  });
};

export const useDeleteJob = () => {
  const { authAxios } = useAuth();
  const toast = useToast();
  return useMutation({
    mutationFn: (id) => authAxios.delete(`/api/v1/recruiter/jobs/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recruiter_jobs'] });
      toast('Job deleted', 'success');
    },
  });
};

// Backend.jsx — useSubmitTest
export const useSubmitTest = (applicationId) => {
  const { authAxios } = useAuth();
  queryClient.invalidateQueries({ queryKey: ['results'] });

  return useMutation({
    mutationFn: async (data) => {
      const submission = {
        answers: {
          [data.level]: {
            question_id: data.question_id,
            response: data.response,
            submitted_at: new Date().toISOString()
          }
        }
      };
      return authAxios.post(`/api/v1/applicant/tests/${applicationId}`, submission);
    },
    onSuccess: () => queryClient.invalidateQueries(['results'])
  });
};

/* ──────────────────────── RESULTS ──────────────────────── */
export const useApplicantResults = () => {
  const { authAxios } = useAuth();
  return useQuery({
    queryKey: ['applications'],
    queryFn: async () => {
      const res = await authAxios.get('/api/v1/applicant/applications');
      return res.data.items.map(app => ({
        ...app,
        job_title: app.job_title || 'Unknown Job',
        outcome: app.outcome || (app.status === 'evaluated' ? 'pending' : '')
      }));
    },
  });
};
/* ──────────────────────── GEMINI PUBLISH ──────────────────────── */
export const usePublishGemini = () => {
  const { authAxios } = useAuth();
  const toast = useToast();
  return useMutation({
    mutationFn: (applicationId) => authAxios.post(`/api/v1/recruiter/applications/${applicationId}/publish-gemini`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applicants'] });
      toast('Published via Gemini', 'success');
    },
  });
};

/* ──────────────────────── MESSAGING HISTORY ──────────────────────── */
export const useMessageHistory = (otherUserId) => {
  const { authAxios } = useAuth();
  return useQuery({
    queryKey: ['messages', otherUserId],
    queryFn: async () => {
      const res = await authAxios.get(`/api/v1/messages/${otherUserId}`);
      return res.data.items.map(m => ({
        id: m._id,
        sender_id: m.sender_id,
        content: m.content,
        timestamp: new Date(m.timestamp).getTime(),
      }));
    },
    enabled: !!otherUserId,
  });
};

/* ──────────────────────── PDF EXPORT ──────────────────────── */
export const exportToPDF = async (elementId, filename) => {
  const el = document.getElementById(elementId);
  if (!el) return;
  const canvas = await html2canvas(el);
  const img = canvas.toDataURL('image/png');
  const pdf = new jsPDF({ orientation: 'landscape' });
  const w = pdf.internal.pageSize.getWidth();
  const h = (canvas.height * w) / canvas.width;
  pdf.addImage(img, 'PNG', 0, 0, w, h);
  pdf.save(`${filename}.pdf`);
};