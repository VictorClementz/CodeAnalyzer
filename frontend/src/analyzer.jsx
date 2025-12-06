import { useState } from 'react';
import './analyzer.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function CodeAnalyzer() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeCode = async () => {
    if (!code.trim()) {
      setError('Please paste some code to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:5002/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to analyze code. Make sure the backend server is running on port 5002.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
  };

  return (
    <div className="analyzer-container">
      <header className="header">
        <div className="header-content">
          <h1 className="title">Code Readability Analyzer</h1>
          <p className="subtitle">Quantify your code's maintainability and clarity</p>
        </div>
      </header>

      <main className="main-content">
        <div className="input-section">
          <div className="controls">
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>
            
            <button 
              onClick={analyzeCode} 
              disabled={loading || !code.trim()}
              className="analyze-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>
          </div>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            className="code-input"
            spellCheck="false"
          />
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {results && (
          <div className="results-section">
            <div className="score-card">
              <div className="score-label">Readability Score</div>
              <div className={`score-value ${getScoreColor(results.readability_score)}`}>
                {results.readability_score}
                <span className="score-max">/100</span>
              </div>
              <div className="score-description">
                {results.readability_score >= 80 && 'Excellent - Highly maintainable'}
                {results.readability_score >= 60 && results.readability_score < 80 && 'Good - Well structured'}
                {results.readability_score >= 40 && results.readability_score < 60 && 'Fair - Room for improvement'}
                {results.readability_score < 40 && 'Needs work - Consider refactoring'}
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">Cyclomatic Complexity</div>
                <div className="metric-value">{results.cyclomatic_complexity || 'N/A'}</div>
                <div className="metric-description">Number of execution paths</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Maintainability Index</div>
                <div className="metric-value">{results.maintainability_index || 'N/A'}</div>
                <div className="metric-description">Industry standard metric</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Lines of Code</div>
                <div className="metric-value">{results.lines_of_code || 'N/A'}</div>
                <div className="metric-description">Total line count</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Comment Density</div>
                <div className="metric-value">{results.comment_density ? `${results.comment_density}%` : 'N/A'}</div>
                <div className="metric-description">Documentation coverage</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Duplication Percentage</div>
                <div className="metric-value">{results.duplication_percentage ? `${results.duplication_percentage}%` : 'N/A'}</div>
                <div className="metric-description">Documentation coverage</div>
              </div>
            </div>

            
            


            

            {results.suggestions && results.suggestions.length > 0 && (
              <div className="suggestions-section">
                <h3 className="suggestions-title">Suggestions for Improvement</h3>
                <ul className="suggestions-list">
                  {results.suggestions.map((suggestion, index) => (
                    <li key={index} className="suggestion-item">{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built with React + Flask • Powered by Radon</p>
      </footer>
    </div>
  );
}

export default CodeAnalyzer;