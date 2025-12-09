import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchWithAuth } from '../utils/auth';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './FileHistory.css';

function FileHistory() {
  const { projectId, fileId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadHistory();
  }, [projectId, fileId]);

  const loadHistory = async () => {
    try {
      const response = await fetchWithAuth(`/projects/${projectId}/files/${fileId}/history`);
      if (!response.ok) throw new Error('Failed to load history');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading history...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!data) return <div className="error-message">No data found</div>;

  // Prepare chart data (reverse to show oldest first)
  const chartData = [...data.analyses].reverse().map(a => ({
    date: new Date(a.timestamp).toLocaleDateString(),
    score: a.readability_score,
    complexity: a.cyclomatic_complexity,
    maintainability: a.maintainability_index
  }));

  return (
    <div className="file-history-container">
      <header className="file-history-header">
        <Link to={`/projects/${projectId}`} className="back-link">
          ← Back to Project
        </Link>
        <h1>{data.file.filename}</h1>
        <span className="file-language-badge">{data.file.language}</span>
      </header>

      {data.analyses.length === 0 ? (
        <p>No analysis history yet</p>
      ) : (
        <>
          <section className="chart-section">
            <h2>Readability Score Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#ff6b35" 
                  strokeWidth={3}
                  name="Readability Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </section>

          <section className="chart-section">
            <h2>Complexity & Maintainability</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="complexity" 
                  stroke="#6c5ce7" 
                  strokeWidth={2}
                  name="Complexity"
                />
                <Line 
                  type="monotone" 
                  dataKey="maintainability" 
                  stroke="#00d9ff" 
                  strokeWidth={2}
                  name="Maintainability"
                />
              </LineChart>
            </ResponsiveContainer>
          </section>

          <section className="history-table">
            <h2>Analysis History</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Commit</th>
                    <th>Score</th>
                    <th>Complexity</th>
                    <th>Maintainability</th>
                    <th>LOC</th>
                  </tr>
                </thead>
                <tbody>
                  {data.analyses.map(analysis => (
                    <tr key={analysis.id}>
                      <td>{new Date(analysis.timestamp).toLocaleString()}</td>
                      <td>
                        {analysis.commit_hash ? (
                          <code>{analysis.commit_hash.substring(0, 7)}</code>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className={`score-${getScoreClass(analysis.readability_score)}`}>
                        {analysis.readability_score.toFixed(1)}
                      </td>
                      <td>{analysis.cyclomatic_complexity}</td>
                      <td>{analysis.maintainability_index.toFixed(1)}</td>
                      <td>{analysis.lines_of_code}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'fair';
  return 'poor';
}

export default FileHistory;