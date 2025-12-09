import { useState } from 'react';
import './analyzer.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function CodeAnalyzer() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [results, setResults] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('single');
  const [isDragging, setIsDragging] = useState(false);

  const analyzeCode = async () => {
    if (!code.trim()) {
      setError('Please paste some code to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setBatchResults(null);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
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
      setMode('single');
    } catch (err) {
      setError('Failed to analyze code. Make sure the backend server is running on port 5002.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeBatchFiles = async (files) => {
    if (files.length === 0) {
      setError('Please select files to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setBatchResults(null);

    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files', file));
    formData.append('language', language);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze-batch`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Batch analysis failed');
      }

      const data = await response.json();
      setBatchResults(data);
      setMode('batch');
    } catch (err) {
      setError('Failed to analyze files. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchUpload = async (e) => {
    analyzeBatchFiles(e.target.files);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    analyzeBatchFiles(files);
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
          <h1 className="title"></h1>
          <p className="subtitle">Quantify your code's maintainability and clarity(only python rn)</p>
        </div>
      </header>

      <main className="main-content">
        <div className="left-section">
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

              <label className="analyze-button" style={{ cursor: 'pointer', textAlign: 'center' }}>
                {loading ? 'Uploading...' : 'Upload Files'}
                <input 
                  type="file" 
                  multiple
                  accept=".py,.js,.java,.cpp"
                  onChange={handleBatchUpload}
                  disabled={loading}
                  style={{ display: 'none' }}
                />
              </label>
            </div>

            <div
              className={`code-input-wrapper ${isDragging ? 'dragging' : ''}`}
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your code here or drag & drop files..."
                className="code-input"
                spellCheck="false"
              />
              {isDragging && (
                <div className="drag-overlay">
                  <div className="drag-message">Drop files here to analyze</div>
                </div>
              )}
            </div>
          </div>

          {(results || batchResults) && (
            <div className="score-card">
              <div className="score-label">
                {mode === 'batch' ? 'Project Readability Score' : 'Readability Score'}
              </div>
              <div className={`score-value ${getScoreColor(
                mode === 'batch' ? batchResults.avg_readability : results.readability_score
              )}`}>
                {mode === 'batch' ? batchResults.avg_readability : results.readability_score}
                <span className="score-max">/100</span>
              </div>
              <div className="score-description">
                {mode === 'batch' && `Analyzed ${batchResults.total_files} files`}
                {mode === 'single' && (
                  <>
                    {results.readability_score >= 80 && 'Excellent (For now)'}
                    {results.readability_score >= 60 && results.readability_score < 80 && 'Good (enough, git merge origin main --force)'}
                    {results.readability_score >= 40 && results.readability_score < 60 && 'ChatGPT: Refactor this code'}
                    {results.readability_score < 40 && 'Shit spaghetti code'}
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {mode === 'single' && results && (
          <div className="results-section">
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
                <div className="metric-description">Duplication coverage</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Average Variable Length</div>
                <div className="metric-value">{results.avg_name_length || 'N/A'}</div>
                <div className="metric-description">Variable naming quality</div>
              </div>

              <div className="metric-card" style={{ gridColumn: 'span 2' }}>
                <div className="metric-label">Variable Name Lengths</div>
                <div className="metric-description">Distribution of name lengths</div>
                {results.sorted_name_lengths && results.sorted_name_lengths.length > 0 ? (
                  <>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'flex-end', 
                      gap: '3px',
                      height: '80px',
                      marginTop: '15px',
                      overflow: 'hidden',
                      padding: '0 10px'
                    }}>
                      {results.sorted_name_lengths.map((length, idx) => (
                        <div
                          key={idx}
                          style={{
                            width: '6px',
                            height: `${(length / Math.max(...results.sorted_name_lengths)) * 100}%`,
                            backgroundColor: length === 1 ? '#ff6b6b' : '#4ecdc4',
                            minHeight: '4px',
                            flexShrink: 0,
                            borderRadius: '2px 2px 0 0'
                          }}
                          title={`Length: ${length}`}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      marginTop: '10px',
                      fontSize: '13px',
                      color: '#666',
                      fontWeight: '500'
                    }}>
                      <span>Min: {Math.min(...results.sorted_name_lengths)}</span>
                      <span>Max: {Math.max(...results.sorted_name_lengths)}</span>
                    </div>
                  </>
                ) : (
                  <div style={{ marginTop: '10px', color: '#999' }}>No data</div>
                )}
              </div>

              <div className="metric-card">
                <div className="metric-label">Max Nesting Depth</div>
                <div className="metric-value">{results.max_nesting_depth || 'N/A'}</div>
                <div className="metric-description">Deepest code nesting level</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Avg Nesting Depth</div>
                <div className="metric-value">{results.avg_nesting_depth || 'N/A'}</div>
                <div className="metric-description">Average nesting level</div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Cognitive Complexity</div>
                <div className="metric-value">{results.cognitive_complexity || 'N/A'}</div>
                <div className="metric-description">Difficulty to understand</div>
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

       {mode === 'batch' && batchResults && (
  <div className="results-section">
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-label">Total Files</div>
        <div className="metric-value">{batchResults.total_files}</div>
        <div className="metric-description">Files analyzed</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Total Lines</div>
        <div className="metric-value">{batchResults.total_lines}</div>
        <div className="metric-description">Total project lines</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Complexity</div>
        <div className="metric-value">{batchResults.avg_complexity}</div>
        <div className="metric-description">Cyclomatic complexity</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Maintainability</div>
        <div className="metric-value">{batchResults.avg_maintainability}</div>
        <div className="metric-description">Maintainability index</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Comment Density</div>
        <div className="metric-value">{batchResults.avg_comment_density}%</div>
        <div className="metric-description">Documentation coverage</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Duplication</div>
        <div className="metric-value">{batchResults.avg_duplication}%</div>
        <div className="metric-description">Code duplication</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Variable Length</div>
        <div className="metric-value">{batchResults.avg_name_length}</div>
        <div className="metric-description">Variable naming</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Max Nesting Depth</div>
        <div className="metric-value">{batchResults.max_nesting_depth}</div>
        <div className="metric-description">Deepest nesting in project</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Nesting Depth</div>
        <div className="metric-value">{batchResults.avg_nesting_depth}</div>
        <div className="metric-description">Average nesting level</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Cognitive Complexity</div>
        <div className="metric-value">{batchResults.avg_cognitive_complexity}</div>
        <div className="metric-description">Understanding difficulty</div>
      </div>
    </div>

            <div className="suggestions-section">
              <h3 className="suggestions-title">File Analysis Results</h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {batchResults.files.map((file, idx) => (
                  <div key={idx} style={{ 
                    padding: '1rem', 
                    marginBottom: '1rem',
                    background: 'var(--color-bg)',
                    borderRadius: '6px',
                    borderLeft: `3px solid ${file.error ? 'var(--color-error)' : 'var(--color-accent)'}`
                  }}>
                    <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                      {file.filename}
                    </div>
                    {file.error ? (
                      <div style={{ color: 'var(--color-error)', fontSize: '0.875rem' }}>
                        Error: {file.error}
                      </div>
                    ) : (
                      <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                        Score: {file.metrics.readability_score} | 
                        Lines: {file.metrics.lines_of_code} | 
                        Complexity: {file.metrics.cyclomatic_complexity}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>In development</p>
      </footer>
    </div>
  );
}

export default CodeAnalyzer;