import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../utils/Auth';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const user = authService.getUser();
  const isAuthenticated = authService.isAuthenticated();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          Code Analyzer
        </Link>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <Link to="/">Analyze</Link>
              <Link to="/dashboard">Dashboard</Link>
              <span className="navbar-user">{user?.name}</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/signup">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;