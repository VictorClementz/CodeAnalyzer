import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchWithAuth } from '../utils/auth';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './ProjectDetail.css';

function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await fetchWithAuth(`/projects/${projectId}`);
      if (!response.ok) throw new Error('Failed to load project');
      const data = await response.json();
      setProject(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading project...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!project) return <div className="error-message">Project not found</div>;

  const avgScore = project.files.length > 0
    ? (project.files.reduce((sum, f) => sum + (f.current_score || 0), 0) / project.files.length).toFixed(2)
    : 'N/A';

  return (
    <div className="project-detail-container">
      <header className="project-detail-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1>{project.name}</h1>
        <div className="project-stats">
          <div className="stat-card">
            <div className="stat-label">Files</div>
            <div className="stat-value">{project.files.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg Score</div>
            <div className="stat-value">{avgScore}</div>
          </div>
        </div>
      </header>

      <div className="files-section">
        <h2>Files</h2>
        {project.files.length === 0 ? (
          <p>No files analyzed yet</p>
        ) : (
          <div className="files-grid">
            {project.files.map(file => (
              <Link
                key={file.id}
                to={`/projects/${projectId}/files/${file.id}`}
                className="file-card"
              >
                <div className="file-name">{file.filename}</div>
                <div className="file-meta">
                  <span className="file-language">{file.language}</span>
                  <span className={`file-score score-${getScoreClass(file.current_score)}`}>
                    {file.current_score ? file.current_score.toFixed(1) : 'N/A'}
                  </span>
                </div>
                <div className="file-stats">
                  <span>{file.total_analyses} analyses</span>
                  {file.last_analyzed && (
                    <span>Last: {new Date(file.last_analyzed).toLocaleDateString()}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'fair';
  return 'poor';
}

export default ProjectDetail;