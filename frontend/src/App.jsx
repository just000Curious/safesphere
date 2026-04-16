import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import UserPanel from './pages/UserPanel';
import ContactsPanel from './pages/ContactsPanel';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { ToastProvider, ToastContext } from './context/ToastContext';

// Identity Route wrapper
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, loading } = React.useContext(AuthContext);
  
  if (loading) return <div className="min-h-screen flex items-center justify-center p-20 animate-pulse text-primary tracking-widest uppercase">Decoupling Global Security Key...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireAdmin && user.role !== 'admin') return <Navigate to="/" replace />;
  
  return children;
};

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
        <Routes>
          {/* Public Identity Portals */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={<Layout />}>
            {/* Authenticated Global Views */}
            <Route index element={
              <ProtectedRoute>
                <UserPanel />
              </ProtectedRoute>
            } />
            <Route path="contacts" element={
              <ProtectedRoute>
                <ContactsPanel />
              </ProtectedRoute>
            } />
            
            {/* Strict Admin Hierarchy Overrides */}
            <Route path="dashboard" element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </ToastProvider>
  );
}

export default App;
