import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchWithAuth } from '../utils/auth';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await fetchWithAuth('/projects');
      if (!response.ok) throw new Error('Failed to load projects');
      const data = await response.json();
      console.log('Project data:', data);
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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