import React, { createContext, useState, useEffect } from 'react';

export const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[200] flex flex-col gap-2">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className={`px-4 py-3 rounded-lg shadow-xl border animate-slide-up bg-black/80 backdrop-blur-md text-white min-w-[200px] flex items-center gap-3 ${
              toast.type === 'error' ? 'border-danger/50 text-danger' : 
              toast.type === 'warning' ? 'border-warning/50 text-warning' : 
              'border-success/50 text-success'
            }`}
          >
            <div className={`w-2 h-2 rounded-full ${toast.type === 'error' ? 'bg-danger animate-pulse' : toast.type==='warning' ? 'bg-warning animate-ping' : 'bg-success'}`}></div>
            <span className="text-sm font-medium tracking-wide text-white">{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
