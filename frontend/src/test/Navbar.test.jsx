import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Navbar from '../Components/Navbar';
import { authService } from '../utils/Auth';

// Mock the authService
vi.mock('../utils/Auth', () => ({
  authService: {
    getUser: vi.fn(),
    isAuthenticated: vi.fn(),
    logout: vi.fn(),
  }
}));

const renderNavbar = () => {
  return render(
    <BrowserRouter>
      <Navbar />
    </BrowserRouter>
  );
};

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the brand name', () => {
    authService.isAuthenticated.mockReturnValue(false);
    authService.getUser.mockReturnValue(null);

    renderNavbar();

    expect(screen.getByText('Code Analyzer')).toBeInTheDocument();
  });

  it('should show login and signup links when not authenticated', () => {
    authService.isAuthenticated.mockReturnValue(false);
    authService.getUser.mockReturnValue(null);

    renderNavbar();

    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
    expect(screen.queryByText('Logout')).not.toBeInTheDocument();
  });

  it('should show dashboard and logout when authenticated', () => {
    authService.isAuthenticated.mockReturnValue(true);
    authService.getUser.mockReturnValue({ name: 'Test User', email: 'test@example.com' });

    renderNavbar();

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
    expect(screen.queryByText('Sign Up')).not.toBeInTheDocument();
  });

  it('should display user name when authenticated', () => {
    authService.isAuthenticated.mockReturnValue(true);
    authService.getUser.mockReturnValue({ name: 'John Doe', email: 'john@example.com' });

    renderNavbar();

    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('should call logout when logout button is clicked', async () => {
    authService.isAuthenticated.mockReturnValue(true);
    authService.getUser.mockReturnValue({ name: 'Test User' });

    renderNavbar();

    const logoutButton = screen.getByText('Logout');
    await userEvent.click(logoutButton);

    expect(authService.logout).toHaveBeenCalled();
  });

  it('should show Analyze link when authenticated', () => {
    authService.isAuthenticated.mockReturnValue(true);
    authService.getUser.mockReturnValue({ name: 'Test User' });

    renderNavbar();

    const analyzeLinks = screen.getAllByText('Analyze');
    expect(analyzeLinks.length).toBeGreaterThan(0);
  });
});
