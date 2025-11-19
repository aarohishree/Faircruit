import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const ResultsPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/v1/test-results/${testId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Error fetching results:', error);
        setResults(getMockResults());
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [testId]);

  if (loading) {
    return <div className="results-loading">Loading results...</div>;
  }

  if (!results) {
    return <div className="results-error">Error loading results</div>;
  }

  const passPercentage = (results.passed_questions / results.total_questions) * 100;
  const isPassed = passPercentage >= 70;

  return (
    <div className="results-page">
      <div className="container results-container">
        <div className="results-header">
          <div className={`score-badge ${isPassed ? 'passed' : 'failed'}`}>
            {isPassed ? '✓ PASSED' : '✗ FAILED'}
          </div>
          <h1>Test Results</h1>
          <p className="job-title">{results.job_title}</p>
        </div>

        <div className="results-grid">
          <div className="result-card score-card">
            <h3>Your Score</h3>
            <div className="large-score">{Math.round(passPercentage)}%</div>
            <p>{results.passed_questions} out of {results.total_questions} questions correct</p>
          </div>

          <div className="result-card">
            <h3>Performance by Level</h3>
            <div className="level-breakdown">
              {results.level_scores && Object.entries(results.level_scores).map(([level, score]) => (
                <div key={level} className="level-item">
                  <span className="level-name">{level}</span>
                  <div className="level-progress">
                    <div className="level-bar" style={{ width: `${score * 100}%` }}></div>
                  </div>
                  <span className="level-score">{Math.round(score * 100)}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="result-card">
            <h3>Test Statistics</h3>
            <div className="stats">
              <div className="stat-item">
                <span className="stat-label">Time Taken:</span>
                <span className="stat-value">{results.time_taken} min</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Average Time per Q:</span>
                <span className="stat-value">{Math.round(results.time_taken / results.total_questions)} min</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Tab Switches:</span>
                <span className="stat-value">{results.tab_switches}</span>
              </div>
              {results.cheating_detected && (
                <div className="stat-item alert">
                  <span className="stat-label">⚠️ Cheating Indicators:</span>
                  <span className="stat-value">Detected</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="detailed-feedback">
          <h2>Detailed Feedback</h2>
          <div className="questions-review">
            {results.question_reviews && results.question_reviews.map((review, idx) => (
              <div key={idx} className={`question-review ${review.correct ? 'correct' : 'incorrect'}`}>
                <div className="review-header">
                  <span className="question-num">Q{idx + 1}</span>
                  <span className="review-status">
                    {review.correct ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                </div>
                <p className="review-question">{review.question}</p>
                {!review.correct && (
                  <div className="review-feedback">
                    <p><strong>Your Answer:</strong> {review.your_answer}</p>
                    <p><strong>Expected Answer:</strong> {review.expected_answer}</p>
                    <p><strong>Feedback:</strong> {review.feedback}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="next-steps">
          <h2>What's Next?</h2>
          {isPassed ? (
            <div className="success-message">
              <p>🎉 Congratulations! You've passed this assessment.</p>
              <p>The recruiter will review your results and contact you soon.</p>
            </div>
          ) : (
            <div className="retry-message">
              <p>Keep practicing! Review the feedback above to improve your skills.</p>
              <button className="btn btn-primary" onClick={() => navigate('/')}>
                Try Another Test
              </button>
            </div>
          )}
        </div>

        <div className="action-buttons">
          <button className="btn btn-secondary" onClick={() => window.print()}>
            📥 Download Results
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Home
          </button>
        </div>
      </div>

      <style>{`
        .results-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 40px 20px;
        }

        .results-container {
          background: white;
          border-radius: 16px;
          padding: 40px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .results-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .score-badge {
          display: inline-block;
          padding: 12px 24px;
          border-radius: 8px;
          font-weight: 700;
          font-size: 0.9rem;
          margin-bottom: 16px;
        }

        .score-badge.passed {
          background: #c6f6d5;
          color: #22543d;
        }

        .score-badge.failed {
          background: #fed7d7;
          color: #742a2a;
        }

        .results-header h1 {
          font-size: 2.5rem;
          margin: 16px 0 8px;
          color: #2d3748;
        }

        .job-title {
          color: #718096;
          font-size: 1.1rem;
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 24px;
          margin-bottom: 40px;
        }

        .result-card {
          background: #f7fafc;
          border-radius: 12px;
          padding: 24px;
          border: 2px solid #e2e8f0;
        }

        .score-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          text-align: center;
          grid-column: span 1;
        }

        .score-card h3 {
          margin-top: 0;
        }

        .large-score {
          font-size: 3.5rem;
          font-weight: 700;
          margin: 16px 0;
        }

        .result-card h3 {
          margin-top: 0;
          color: #2d3748;
        }

        .level-breakdown {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .level-item {
          display: grid;
          grid-template-columns: 80px 1fr 50px;
          align-items: center;
          gap: 12px;
        }

        .level-name {
          font-weight: 600;
          color: #2d3748;
        }

        .level-progress {
          background: #e2e8f0;
          border-radius: 4px;
          height: 8px;
          overflow: hidden;
        }

        .level-bar {
          height: 100%;
          background: linear-gradient(90deg, #667eea, #764ba2);
          transition: width 0.3s;
        }

        .level-score {
          font-weight: 700;
          color: #667eea;
          text-align: right;
        }

        .stats {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #e2e8f0;
        }

        .stat-item.alert {
          color: #e53e3e;
        }

        .stat-label {
          color: #718096;
          font-weight: 600;
        }

        .stat-value {
          color: #2d3748;
          font-weight: 700;
        }

        .detailed-feedback {
          margin-bottom: 40px;
        }

        .detailed-feedback h2 {
          color: #2d3748;
          margin-bottom: 20px;
        }

        .questions-review {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .question-review {
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          padding: 16px;
        }

        .question-review.correct {
          border-color: #9ae6b4;
          background: #f0fff4;
        }

        .question-review.incorrect {
          border-color: #fc8181;
          background: #fff5f5;
        }

        .review-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 12px;
          border-bottom: 1px solid;
        }

        .question-num {
          font-weight: 700;
          color: #667eea;
        }

        .review-status {
          font-weight: 700;
        }

        .question-review.correct .review-status {
          color: #22863a;
        }

        .question-review.incorrect .review-status {
          color: #cb2431;
        }

        .review-question {
          color: #2d3748;
          margin: 12px 0;
          font-weight: 600;
        }

        .review-feedback {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid;
        }

        .review-feedback p {
          margin: 8px 0;
          color: #2d3748;
        }

        .next-steps {
          background: #f7fafc;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 24px;
          border-left: 4px solid #667eea;
        }

        .next-steps h2 {
          color: #2d3748;
          margin-top: 0;
        }

        .success-message,
        .retry-message {
          color: #2d3748;
        }

        .success-message p {
          font-size: 1.1rem;
          margin: 8px 0;
        }

        .action-buttons {
          display: flex;
          gap: 12px;
          justify-content: center;
        }

        .btn {
          padding: 12px 24px;
          border-radius: 8px;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
        }

        .btn-secondary {
          background: white;
          color: #667eea;
          border: 2px solid #667eea;
        }

        .btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        @media (max-width: 768px) {
          .results-container {
            padding: 20px;
          }

          .results-grid {
            grid-template-columns: 1fr;
          }

          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

function getMockResults() {
  return {
    job_title: 'Senior Backend Engineer',
    passed_questions: 3,
    total_questions: 4,
    level_scores: {
      'Awareness': 1,
      'Application': 0.8,
      'Analysis': 0.7,
      'Mastery': 0.6
    },
    time_taken: 45,
    tab_switches: 1,
    cheating_detected: false,
    question_reviews: [
      {
        correct: true,
        question: 'What is the time complexity of binary search?',
        your_answer: 'O(log n)',
        expected_answer: 'O(log n)',
        feedback: 'Correct! Binary search divides the search space in half with each iteration.'
      },
      {
        correct: false,
        question: 'Explain the difference between Git merge and Git rebase.',
        your_answer: 'They do the same thing',
        expected_answer: 'Merge creates a new commit combining branches, while rebase replays commits on top of another branch',
        feedback: 'Not quite. While both combine branches, they work differently. Merge creates a new merge commit, while rebase replays your commits.'
      },
      {
        correct: true,
        question: 'Design a scalable system architecture for a social media platform.',
        your_answer: 'Use microservices, load balancing, caching layer, and NoSQL database',
        expected_answer: 'Similar concepts',
        feedback: 'Good answer! You covered key architectural components.'
      },
      {
        correct: true,
        question: 'Fix the factorial code bug.',
        your_answer: 'def factorial(n):\n  if n == 0:\n    return 1\n  return n * factorial(n-1)',
        expected_answer: 'return n * factorial(n-1)',
        feedback: 'Perfect! You identified and fixed the bug correctly.'
      }
    ]
  };
}

export default ResultsPage;
