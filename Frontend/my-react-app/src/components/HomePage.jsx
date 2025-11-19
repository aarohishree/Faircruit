import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../Backend.jsx';

const HomePage = () => {
  const [jobs, setJobs] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { isLoggedIn, user } = useAuth();

  const roles = [
    "Software Engineer",
    "Data Scientist",
    "Product Manager",
    "DevOps Engineer",
    "UX Designer",
    "Security Engineer",
    "Business Analyst"
  ];

  useEffect(() => {
    // Fetch jobs from backend
    const fetchJobs = async () => {
      try {
        const response = await fetch('/api/v1/jobs');
        const data = await response.json();
        setJobs(data.jobs || []);
        setFiltered(data.jobs || []);
      } catch (error) {
        console.error('Error fetching jobs:', error);
        // Use mock data if backend fails
        setJobs(getMockJobs());
        setFiltered(getMockJobs());
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  useEffect(() => {
    let result = jobs;

    if (searchTerm) {
      result = result.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedRole) {
      result = result.filter(job => job.role === selectedRole);
    }

    setFiltered(result);
  }, [searchTerm, selectedRole, jobs]);

  const handleStartTest = (jobId) => {
    if (!isLoggedIn) {
      navigate('/get-started');
      return;
    }
    navigate(`/test/${jobId}`);
  };

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="container">
          <h1>Find Your Perfect Role</h1>
          <p>Take skill-based assessments and land your dream job</p>
          
          <div className="search-filters">
            <input
              type="text"
              placeholder="Search jobs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="role-filter"
            >
              <option value="">All Roles</option>
              {roles.map(role => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="jobs-section">
        <div className="container">
          {loading ? (
            <div className="loading">Loading jobs...</div>
          ) : filtered.length === 0 ? (
            <div className="no-jobs">No jobs found. Try adjusting your filters.</div>
          ) : (
            <div className="jobs-grid">
              {filtered.map(job => (
                <div key={job.id} className="job-card">
                  <div className="job-header">
                    <h3>{job.title}</h3>
                    <span className="role-badge">{job.role}</span>
                  </div>
                  
                  <p className="job-description">{job.description.substring(0, 150)}...</p>
                  
                  <div className="job-meta">
                    <div className="meta-item">
                      <span className="label">Questions:</span>
                      <span className="value">{job.num_questions || 4}</span>
                    </div>
                    <div className="meta-item">
                      <span className="label">Duration:</span>
                      <span className="value">{job.duration_minutes || 60} min</span>
                    </div>
                  </div>

                  <button
                    className="btn btn-primary start-test-btn"
                    onClick={() => handleStartTest(job.id)}
                  >
                    Start Test
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        .home-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .hero-section {
          padding: 60px 20px;
          text-align: center;
          color: white;
        }

        .hero-section h1 {
          font-size: 3rem;
          margin-bottom: 10px;
          font-weight: 700;
        }

        .hero-section p {
          font-size: 1.2rem;
          margin-bottom: 30px;
          opacity: 0.9;
        }

        .search-filters {
          display: flex;
          gap: 10px;
          max-width: 600px;
          margin: 0 auto;
          flex-wrap: wrap;
          justify-content: center;
        }

        .search-input, .role-filter {
          padding: 12px 20px;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          flex: 1;
          min-width: 250px;
        }

        .role-filter {
          min-width: 200px;
        }

        .jobs-section {
          padding: 60px 20px;
          background: #f5f7fa;
        }

        .jobs-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 24px;
        }

        .job-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s, box-shadow 0.3s;
          display: flex;
          flex-direction: column;
        }

        .job-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }

        .job-header {
          display: flex;
          justify-content: space-between;
          align-items: start;
          margin-bottom: 12px;
        }

        .job-header h3 {
          margin: 0;
          font-size: 1.3rem;
          color: #2d3748;
        }

        .role-badge {
          background: #667eea;
          color: white;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 0.85rem;
          white-space: nowrap;
        }

        .job-description {
          color: #718096;
          margin: 12px 0;
          line-height: 1.6;
          flex-grow: 1;
        }

        .job-meta {
          display: flex;
          gap: 20px;
          margin: 16px 0;
          padding: 12px 0;
          border-top: 1px solid #e2e8f0;
          border-bottom: 1px solid #e2e8f0;
        }

        .meta-item {
          display: flex;
          flex-direction: column;
        }

        .meta-item .label {
          font-size: 0.85rem;
          color: #a0aec0;
          font-weight: 600;
        }

        .meta-item .value {
          font-size: 1.1rem;
          color: #2d3748;
          font-weight: 700;
        }

        .start-test-btn {
          margin-top: auto;
          width: 100%;
          padding: 12px;
        }

        .loading, .no-jobs {
          text-align: center;
          padding: 40px;
          font-size: 1.1rem;
          color: #718096;
        }
      `}</style>
    </div>
  );
};

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
    },
    {
      id: '4',
      title: 'DevOps Engineer',
      role: 'DevOps Engineer',
      description: 'Manage cloud infrastructure on AWS/GCP. Kubernetes, Docker, and CI/CD pipeline expertise needed.',
      num_questions: 4,
      duration_minutes: 75
    },
    {
      id: '5',
      title: 'Security Engineer',
      role: 'Security Engineer',
      description: 'Design and implement security solutions. Penetration testing and vulnerability assessment skills required.',
      num_questions: 4,
      duration_minutes: 90
    },
    {
      id: '6',
      title: 'Product Manager',
      role: 'Product Manager',
      description: 'Drive product strategy and roadmap. Strong analytical and communication skills essential.',
      num_questions: 4,
      duration_minutes: 60
    }
  ];
}

export default HomePage;
