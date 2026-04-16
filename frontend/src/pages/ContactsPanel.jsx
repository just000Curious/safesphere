import React, { useState, useEffect } from 'react';
import { UserPlus, Trash2, Phone, Mail, ShieldAlert } from 'lucide-react';
import api from '../api';

export default function ContactsPanel() {
  const [contacts, setContacts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    relationship: 'family',
    is_primary: false
  });

  const fetchContacts = async () => {
    try {
      const response = await api.get('/users/contacts');
      setContacts(response.data);
    } catch (error) {
      console.error("Error fetching contacts", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      // Fix Pydantic 422: Scrub empty string into semantic null
      const payload = { ...formData };
      if (!payload.email || payload.email.trim() === '') {
        payload.email = null;
      }
      
      await api.post('/users/contacts', payload);
      setFormData({ name: '', phone: '', email: '', relationship: 'family', is_primary: false });
      fetchContacts();
    } catch (error) {
      console.error("Error adding contact", error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/users/contacts/${id}`);
      fetchContacts();
    } catch (error) {
      console.error("Error deleting contact", error);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Contact List */}
      <div className="lg:col-span-2 space-y-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="text-primary" /> Trusted Contacts
        </h2>
        
        {isLoading ? (
          <div className="glass-panel p-8 text-center text-textMuted animate-pulse">Loading contacts...</div>
        ) : contacts.length === 0 ? (
          <div className="glass-panel p-8 text-center border-dashed">
            <p className="text-textMuted mb-2">No trusted contacts added yet.</p>
            <p className="text-sm">These contacts will be instantly notified during an emergency.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {contacts.map((contact) => (
              <div key={contact.id} className="glass-panel p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-bold text-lg text-white">{contact.name}</h3>
                    {contact.is_primary && (
                      <span className="bg-primary/20 text-primary text-xs px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                        Primary
                      </span>
                    )}
                    <span className="bg-white/5 text-textMuted text-xs px-2 py-0.5 rounded-full capitalize">
                      {contact.relationship}
                    </span>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2 sm:gap-6 text-sm text-textMuted mt-2">
                    <span className="flex items-center gap-2"><Phone size={14} />{contact.phone}</span>
                    {contact.email && <span className="flex items-center gap-2"><Mail size={14} />{contact.email}</span>}
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(contact.id)}
                  className="p-2 text-textMuted hover:bg-danger/20 hover:text-danger rounded-xl transition-colors self-start sm:self-center"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Contact Form */}
      <div className="lg:col-span-1">
        <div className="glass-panel p-6 sticky top-24">
          <h3 className="font-bold text-white mb-6 flex items-center gap-2">
            <UserPlus size={20} className="text-primary"/> Add New Contact
          </h3>
          
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-sm text-textMuted mb-1">Full Name</label>
              <input 
                required type="text" 
                value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})}
                className="w-full bg-darker/50 border border-white/10 rounded-lg p-2.5 text-white focus:outline-none focus:border-primary transition-colors" 
              />
            </div>
            
            <div>
              <label className="block text-sm text-textMuted mb-1">Phone Number</label>
              <input 
                required type="tel" placeholder="+1234567890"
                value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})}
                className="w-full bg-darker/50 border border-white/10 rounded-lg p-2.5 text-white focus:outline-none focus:border-primary transition-colors" 
              />
            </div>
            
            <div>
              <label className="block text-sm text-textMuted mb-1">Email <span className="text-white/30">(Optional)</span></label>
              <input 
                type="email" 
                value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})}
                className="w-full bg-darker/50 border border-white/10 rounded-lg p-2.5 text-white focus:outline-none focus:border-primary transition-colors" 
              />
            </div>

            <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4 mt-2">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={formData.is_primary} onChange={e => setFormData({...formData, is_primary: e.target.checked})}
                  className="accent-primary w-4 h-4" 
                />
                Primary Contact
              </label>
              <select 
                value={formData.relationship} onChange={e => setFormData({...formData, relationship: e.target.value})}
                className="bg-darker/50 border border-white/10 rounded text-sm text-white p-1"
              >
                <option value="family">Family</option>
                <option value="friend">Friend</option>
                <option value="coworker">Coworker</option>
                <option value="other">Other</option>
              </select>
            </div>

            <button type="submit" className="w-full py-3 mt-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-bold transition-transform active:scale-95 shadow-lg shadow-primary/20">
              Save Contact
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
