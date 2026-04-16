import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ShieldCheck, Lock, Mail, AlertCircle } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await login(email, password);
      if (data.role === 'admin') navigate('/dashboard');
      else navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-darker text-textLight pattern-bg">
      <div className="w-full max-w-md glass-panel p-8 space-y-8 animate-fade-in">
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <ShieldCheck size={48} className="text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-wider text-textEmphasis">SafeSphere</h1>
          <p className="text-textMuted">Authenticate to access emergency grid.</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-danger/10 text-danger border border-danger/20 rounded-lg">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-textMuted mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={18} />
              <input
                type="email"
                required
                className="w-full bg-black/20 border border-white/10 rounded-lg py-2.5 pl-10 px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-textLight"
                placeholder="user@safesphere.local"
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-textMuted mb-2">Security Key</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={18} />
              <input
                type="password"
                required
                className="w-full bg-black/20 border border-white/10 rounded-lg py-2.5 pl-10 px-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-textLight"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-3 rounded-lg transition-colors flex justify-center items-center gap-2"
          >
            Authenticate
          </button>
        </form>

        <div className="text-center text-sm text-textMuted">
          Entity bypass required? <Link to="/register" className="text-primary hover:underline">Register physical node</Link>
        </div>
      </div>
    </div>
  );
}
