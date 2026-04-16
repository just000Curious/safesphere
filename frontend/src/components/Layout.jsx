import React, { useState, useEffect, useContext } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, Users, AlertTriangle, Sun, Moon, LogOut } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

export default function Layout() {
  const location = useLocation();
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
    }
  }, [isDark]);

  const { logout, user } = useContext(AuthContext);

  const navItems = [
    { name: 'User Panel', path: '/', icon: AlertTriangle },
    { name: 'Contacts', path: '/contacts', icon: Users },
  ];
  
  if (user?.role === 'admin') {
    navItems.push({ name: 'Admin Dashboard', path: '/dashboard', icon: LayoutDashboard });
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Persistent Top Navigation Bar */}
      <nav className="border-b border-white/5 glass-panel !rounded-none sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <ShieldCheck className="text-primary" size={28} />
              <span className="font-bold text-xl tracking-wide">SafeSphere</span>
            </Link>

            <div className="flex items-center gap-2 sm:gap-6">
              {/* Navigation Links */}
              <div className="flex items-center gap-1 sm:gap-4 md:gap-8">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive 
                          ? 'bg-primary/20 text-primary' 
                          : 'text-textMuted hover:text-textLight hover:bg-black/5'
                      }`}
                    >
                      <Icon size={18} className={isActive ? "text-primary" : ""} />
                      <span className="hidden sm:inline">{item.name}</span>
                    </Link>
                  );
                })}
              </div>

              {/* Theme Toggle */}
              <button 
                onClick={() => setIsDark(!isDark)}
                className="p-2 ml-2 sm:ml-4 rounded-full bg-black/5 hover:bg-black/10 transition-colors text-textMuted hover:text-textLight"
                title="Toggle Theme"
              >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
              </button>

              {/* Logout Hook */}
              <button 
                onClick={logout}
                className="p-2 rounded-full bg-danger/10 hover:bg-danger/20 transition-colors text-danger hidden sm:flex items-center gap-2 px-4 ml-2 border border-danger/20"
                title="Disconnect Node"
              >
                <LogOut size={16} />
                <span className="text-sm font-bold tracking-wider">LOGOUT</span>
              </button>
              
              {/* Mobile Logout icon only */}
              <button 
                onClick={logout}
                className="p-2 rounded-full bg-danger/10 hover:bg-danger/20 transition-colors text-danger sm:hidden items-center ml-1 border border-danger/20"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Render Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
