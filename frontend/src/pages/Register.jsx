import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ShieldCheck, User, Phone, Mail, Lock, AlertCircle } from 'lucide-react';

export default function Register() {
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', password: '', role: 'user' });
  const [error, setError] = useState('');
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const data = await register(formData);
      if (data.role === 'admin') navigate('/dashboard');
      else navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register node');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-darker text-textLight pattern-bg">
      <div className="w-full max-w-md glass-panel p-8 space-y-8 animate-fade-in overflow-y-auto max-h-screen">
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <ShieldCheck size={40} className="text-primary" />
          </div>
          <h1 className="text-2xl font-bold tracking-wider text-textEmphasis">Register Node</h1>
          <p className="text-textMuted text-sm">Join the SafeSphere Surveillance Grid.</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-danger/10 text-danger border border-danger/20 rounded-lg">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-xs font-medium text-textMuted mb-1">Full Legal Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
              <input type="text" required className="w-full bg-black/20 border border-white/10 rounded-lg py-2 pl-10 px-4 focus:ring-2 focus:ring-primary outline-none text-textLight text-sm" placeholder="John Doe" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-textMuted mb-1">Hardware Identifier (Phone)</label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
              <input type="tel" required className="w-full bg-black/20 border border-white/10 rounded-lg py-2 pl-10 px-4 focus:ring-2 focus:ring-primary outline-none text-textLight text-sm" placeholder="+19999999999" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-textMuted mb-1">Email Directive</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
              <input type="email" required className="w-full bg-black/20 border border-white/10 rounded-lg py-2 pl-10 px-4 focus:ring-2 focus:ring-primary outline-none text-textLight text-sm" placeholder="user@safesphere.local" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-textMuted mb-1">Cryptographic Key</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
              <input type="password" required className="w-full bg-black/20 border border-white/10 rounded-lg py-2 pl-10 px-4 focus:ring-2 focus:ring-primary outline-none text-textLight text-sm" placeholder="••••••••" minLength={6} value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} />
            </div>
          </div>

          <div className="flex gap-4 pt-2">
             <label className="flex items-center gap-2 cursor-pointer">
               <input type="radio" value="user" name="role" checked={formData.role === 'user'} onChange={e => setFormData({...formData, role: 'user'})} className="text-primary focus:ring-primary" />
               <span className="text-sm text-textMuted">Civilian</span>
             </label>
             <label className="flex items-center gap-2 cursor-pointer">
               <input type="radio" value="admin" name="role" checked={formData.role === 'admin'} onChange={e => setFormData({...formData, role: 'admin'})} className="text-danger focus:ring-danger" />
               <span className="text-sm text-textMuted text-danger">Command Dispatcher (Admin)</span>
             </label>
          </div>

          <button type="submit" className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2.5 rounded-lg transition-colors mt-4">
            Initialize Authority
          </button>
        </form>

        <div className="text-center text-sm text-textMuted">
          Entity established? <Link to="/login" className="text-primary hover:underline">Authenticate instead</Link>
        </div>
      </div>
    </div>
  );
}
