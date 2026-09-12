import { useState, useEffect, createContext, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

// ─── Configuration ──────────────────────────────────────
const AUTH_ENDPOINTS = {
  login: '/api/auth/login',
  register: '/api/auth/register',
  refresh: '/api/auth/refresh',
  logout: '/api/auth/logout',
  verify: '/api/auth/verify',
};

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

// ─── Auth Context ────────────────────────────────────────
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isVerified, setIsVerified] = useState(false);

  // 🔄 Restore session on mount
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem(TOKEN_KEY);
      const savedUser = localStorage.getItem(USER_KEY);
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        setIsVerified(true);
      }
    } catch (e) {
      console.warn('⚠️ Failed to restore session:', e);
      logout(true);
    } finally {
      setLoading(false);
    }
  }, []);

  // 💾 Persist session
  const saveSession = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    setIsVerified(true);
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USER_KEY, JSON.stringify(newUser));
  };

  // 🚪 Clear session
  const logout = (skipApi = false) => {
    setToken(null);
    setUser(null);
    setIsVerified(false);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    if (!skipApi) {
      fetch(AUTH_ENDPOINTS.logout, { method: 'POST' }).catch(() => {});
    }
  };

  // 🔑 Login
  const login = async (email, password) => {
    const response = await fetch(AUTH_ENDPOINTS.login, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Login failed');

    saveSession(data.token, data.user);
    return data;
  };

  // 📝 Register
  const register = async (name, email, password) => {
    const response = await fetch(AUTH_ENDPOINTS.register, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Registration failed');

    saveSession(data.token, data.user);
    return data;
  };

  // 📋 Auth Header Helper
  const authHeader = () => ({
    Authorization: token ? `Bearer ${token}` : '',
  });

  return (
    <AuthContext.Provider value={{
      user, token, loading, isVerified,
      login, register, logout, authHeader, saveSession
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// ─── Hook ───────────────────────────────────────────────
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

// ─── Validation ─────────────────────────────────────────
const validateEmail = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const validatePassword = (password) =>
  password.length >= 8;

// ─── Login Component ────────────────────────────────────
export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateEmail(email)) return setError('❌ Invalid email format');
    if (!validatePassword(password)) return setError('❌ Password must be at least 8 characters');

    setIsLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>🔐 Sign In</h2>
      {error && <div style={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.group}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
            placeholder="you@example.com"
            required
          />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{ ...styles.button, ...(isLoading ? styles.buttonDisabled : {}) }}
        >
          {isLoading ? '⏳ Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}

// ─── Register Component ──────────────────────────────────
export function RegisterForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) return setError('❌ Name is required');
    if (!validateEmail(email)) return setError('❌ Invalid email format');
    if (!validatePassword(password)) return setError('❌ Password must be at least 8 characters');
    if (password !== confirmPassword) return setError('❌ Passwords do not match');

    setIsLoading(true);
    try {
      await register(name, email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>📝 Create Account</h2>
      {error && <div style={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.group}>
          <label style={styles.label}>Full Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={styles.input}
            placeholder="John Doe"
            required
          />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
            placeholder="you@example.com"
            required
          />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            placeholder="At least 8 characters"
            required
          />
        </div>

        <div style={styles.group}>
          <label style={styles.label}>Confirm Password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            style={styles.input}
            placeholder="Repeat password"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{ ...styles.button, ...(isLoading ? styles.buttonDisabled : {}) }}
        >
          {isLoading ? '⏳ Creating...' : 'Create Account'}
        </button>
      </form>
    </div>
  );
}

// ─── Protected Route Component ──────────────────────────
export function ProtectedRoute({ children }) {
  const { isVerified, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isVerified) navigate('/login', { replace: true });
  }, [isVerified, loading, navigate]);

  if (loading) return <div style={styles.loading}>⏳ Verifying session...</div>;
  return isVerified ? children : null;
}

// ─── Inline Styles ──────────────────────────────────────
const styles = {
  container: {
    maxWidth: '420px',
    margin: '2rem auto',
    padding: '2rem',
    borderRadius: '12px',
    backgroundColor: '#fff',
    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  },
  heading: {
    textAlign: 'center',
    marginBottom: '1.5rem',
    color: '#1f2937',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  group: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.375rem',
  },
  label: {
    fontSize: '0.9rem',
    fontWeight: 500,
    color: '#374151',
  },
  input: {
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    border: '1px solid #d1d5db',
    fontSize: '1rem',
    transition: 'border-color 0.2s',
  },
  button: {
    marginTop: '0.5rem',
    padding: '0.75rem',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#2563eb',
    color: '#fff',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  buttonDisabled: {
    backgroundColor: '#93c5fd',
    cursor: 'not-allowed',
  },
  error: {
    padding: '0.75rem',
    marginBottom: '1rem',
    borderRadius: '6px',
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    fontSize: '0.9rem',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    color: '#6b7280',
  },
};

export default AuthContext;
