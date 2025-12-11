import { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../utils/Auth';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
   const hasTriggeredImport = useRef(false);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (searchParams.get('import') === 'true' && !hasTriggeredImport.current) {
      hasTriggeredImport.current = true;
      importGit();
    }
  }, [searchParams]);

  const loadProjects = async () => {
    try {
      const response = await fetchWithAuth('/projects');
      if (!response.ok) throw new Error('Failed to load projects');
      const data = await response.json();
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

 const importGit = async () => {
  const name = prompt('New project name:');
  if (!name) return;
  
  try {
    const response = await fetchWithAuth('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    
    if (!response.ok) throw new Error('Failed to create project');
    
    const newProject = await response.json();
    navigate(`/projects/${newProject.id}?linkgit=true`);
  } catch (err) {
    alert('Failed to create project: ' + err.message);
  }
}

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading your projects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Your Projects</h1>
        <p>Track your code quality over time</p>
      </header>

      {projects.length === 0 ? (
        <div className="empty-state">
          <h2>No projects yet</h2>
          <p>Start by analyzing some code on the main page!</p>
          <Link to="/" className="cta-button">Analyze Code</Link>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <Link 
              to={`/projects/${project.id}`} 
              key={project.id} 
              className="project-card"
            >
              <div className="project-header">
                <h3>{project.name}</h3>
                <span className="file-count">{project.file_count} files</span>
              </div>
              <div className="project-date">
                Created {new Date(project.created_at).toLocaleDateString()}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;