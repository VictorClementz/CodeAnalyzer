import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchWithAuth } from '../utils/Auth';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './ProjectDetail.css';

function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Git modal state
  const [showGitModal, setShowGitModal] = useState(false);
  const [gitRepoPath, setGitRepoPath] = useState('');
  const [gitRemoteUrl, setGitRemoteUrl] = useState('');
  
  // Scan state
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);

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

  const linkGitRepo = async () => {
    try {
      const response = await fetchWithAuth(`/projects/${projectId}/git`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_path: gitRepoPath,
          remote_url: gitRemoteUrl,
          auto_detect_git: true
        })
      });
      
      if (response.ok) {
        alert('Git repo linked!');
        loadProject();
        setShowGitModal(false);
        setGitRepoPath('');
        setGitRemoteUrl('');
      } else {
        const data = await response.json();
        alert(`Failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      alert('Failed to link git repo: ' + err.message);
    }
  };

  const scanRepository = async () => {
    if (!confirm('This will analyze all Python files in the linked repository. Continue?')) {
      return;
    }
    
    setScanning(true);
    setScanResult(null);
    
    try {
      const response = await fetchWithAuth(`/projects/${projectId}/scan-repo`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        setScanResult(data);
        loadProject(); // Refresh project data
      } else {
        const data = await response.json();
        alert(`Scan failed: ${data.error}`);
      }
    } catch (err) {
      alert('Failed to scan repository: ' + err.message);
    } finally {
      setScanning(false);
    }
  };

  if (loading) return <div className="loading">Loading project...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!project) return <div className="error-message">Project not found</div>;

  const avgScore = project.files && project.files.length > 0
    ? (project.files.reduce((sum, f) => sum + (f.current_score || 0), 0) / project.files.length).toFixed(2)
    : 'N/A';

  return (
    <div className="project-detail-container">
      <header className="project-detail-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1>{project.project?.name || 'Project'}</h1>
        
        <div className="header-actions">
          <button onClick={() => setShowGitModal(true)} className="git-button">
            ⚙️ Link Git Repo
          </button>
          
          {project.project?.git_repo_path && (
            <button 
              onClick={scanRepository} 
              disabled={scanning}
              className="scan-button"
            >
              {scanning ? '🔄 Scanning...' : '📁 Scan Repository'}
            </button>
          )}
        </div>

        <div className="project-stats">
          <div className="stat-card">
            <div className="stat-label">Files</div>
            <div className="stat-value">{project.files?.length || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg Score</div>
            <div className="stat-value">{avgScore}</div>
          </div>
          {project.project?.git_repo_path && (
            <div className="stat-card">
              <div className="stat-label">Git Repo</div>
              <div className="stat-value" style={{ fontSize: '1rem' }}>✓</div>
            </div>
          )}
        </div>

        {/* Show scan results */}
        {scanResult && (
          <div className="scan-result">
            ✓ {scanResult.message}
            {scanResult.errors && scanResult.errors.length > 0 && (
              <details>
                <summary>{scanResult.errors.length} errors</summary>
                <ul>
                  {scanResult.errors.map((err, i) => (
                    <li key={i}>{err.file}: {err.error}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </header>

      <div className="files-section">
        <h2>Files</h2>
        {!project.files || project.files.length === 0 ? (
          <div className="empty-state">
            <p>No files analyzed yet</p>
            {project.project?.git_repo_path ? (
              <p>Click "Scan Repository" to analyze files from your linked git repo</p>
            ) : (
              <p>Link a git repository or upload files to get started</p>
            )}
          </div>
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

      {/* Git Modal */}
      {showGitModal && (
        <div className="modal-overlay" onClick={() => setShowGitModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Link Git Repository</h2>
            
            <div className="form-group">
              <label>Local Repo Path</label>
              <input
                type="text"
                value={gitRepoPath}
                onChange={(e) => setGitRepoPath(e.target.value)}
                placeholder="/path/to/your/repo"
                className="git-input"
              />
              <small>Absolute path to your local git repository</small>
            </div>

            <div className="form-group">
              <label>Remote URL (Optional)</label>
              <input
                type="text"
                value={gitRemoteUrl}
                onChange={(e) => setGitRemoteUrl(e.target.value)}
                placeholder="https://github.com/user/repo"
                className="git-input"
              />
              <small>GitHub/GitLab URL for reference</small>
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowGitModal(false)} className="cancel-button">
                Cancel
              </button>
              <button onClick={linkGitRepo} className="link-button">
                Link Repository
              </button>
            </div>
          </div>
        </div>
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

export default ProjectDetail;