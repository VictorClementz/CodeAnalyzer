import { describe, it, expect, beforeEach, vi } from 'vitest';
import { authService, fetchWithAuth } from '../utils/Auth';

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe('signup', () => {
    it('should signup successfully and store token', async () => {
      const mockResponse = {
        token: 'test-token',
        user: { id: 1, email: 'test@example.com', name: 'Test User' }
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.signup('test@example.com', 'password', 'Test User');

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user));
    });

    it('should throw error on failed signup', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Email already exists' })
      });

      await expect(authService.signup('test@example.com', 'password', 'Test')).rejects.toThrow('Email already exists');
    });
  });

  describe('login', () => {
    it('should login successfully and store token', async () => {
      const mockResponse = {
        token: 'login-token',
        user: { id: 1, email: 'test@example.com' }
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.login('test@example.com', 'password');

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'login-token');
    });

    it('should throw error on failed login', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Invalid credentials' })
      });

      await expect(authService.login('wrong@example.com', 'wrong')).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('should remove token and user from localStorage', () => {
      authService.logout();

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('user');
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      localStorage.getItem.mockReturnValueOnce('test-token');

      const token = authService.getToken();

      expect(token).toBe('test-token');
      expect(localStorage.getItem).toHaveBeenCalledWith('token');
    });
  });

  describe('getUser', () => {
    it('should return parsed user from localStorage', () => {
      const user = { id: 1, email: 'test@example.com' };
      localStorage.getItem.mockReturnValueOnce(JSON.stringify(user));

      const result = authService.getUser();

      expect(result).toEqual(user);
    });

    it('should return null if no user in localStorage', () => {
      localStorage.getItem.mockReturnValueOnce(null);

      const result = authService.getUser();

      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if token exists', () => {
      localStorage.getItem.mockReturnValueOnce('test-token');

      expect(authService.isAuthenticated()).toBe(true);
    });

    it('should return false if no token', () => {
      localStorage.getItem.mockReturnValueOnce(null);

      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});

describe('fetchWithAuth', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    global.fetch = vi.fn();
    delete window.location;
    window.location = { href: '' };
  });

  it('should add Authorization header when token exists', async () => {
    localStorage.getItem.mockReturnValueOnce('test-token');
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ data: 'test' })
    });

    await fetchWithAuth('/test-endpoint');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token'
        })
      })
    );
  });

  it('should logout and redirect on 401 response', async () => {
    localStorage.getItem.mockReturnValueOnce('expired-token');
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 401
    });

    await expect(fetchWithAuth('/test-endpoint')).rejects.toThrow('Authentication required');
    expect(localStorage.removeItem).toHaveBeenCalledWith('token');
    expect(localStorage.removeItem).toHaveBeenCalledWith('user');
    expect(window.location.href).toBe('/login');
  });

  it('should work without token', async () => {
    localStorage.getItem.mockReturnValueOnce(null);
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200
    });

    await fetchWithAuth('/test-endpoint');

    expect(global.fetch).toHaveBeenCalled();
  });
});
