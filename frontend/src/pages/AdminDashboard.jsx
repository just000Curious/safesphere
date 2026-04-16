import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Clock, Users, ShieldAlert } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [usersGrid, setUsersGrid] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      // Data Retrieval Optimizations: Load instantaneous cache to eliminate layout shifts
      const cachedDashboard = sessionStorage.getItem('dashboardCache');
      if (cachedDashboard) {
        const parsed = JSON.parse(cachedDashboard);
        setStats(parsed.stats);
        setTimeline(parsed.timeline);
        setIncidents(parsed.incidents);
        setUsersGrid(parsed.usersGrid);
        setIsLoading(false); // Instantly unlock UI
      }

      try {
        const [statsRes, timelineRes, incidentsRes, usersRes] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/dashboard/alerts/timeline'),
          api.get('/dashboard/incidents/recent'),
          api.get('/dashboard/users')
        ]);
        
        const formattedTimeline = timelineRes.data.dates.map((date, index) => ({
          date: new Date(date).toLocaleDateString('en-US', { weekday: 'short' }),
          alerts: timelineRes.data.counts[index]
        }));

        // Mutate React state silently
        setStats(statsRes.data);
        setTimeline(formattedTimeline);
        setIncidents(incidentsRes.data);
        setUsersGrid(usersRes.data);
        
        // Formulate Cache Payload
        sessionStorage.setItem('dashboardCache', JSON.stringify({
          stats: statsRes.data,
          timeline: formattedTimeline,
          incidents: incidentsRes.data,
          usersGrid: usersRes.data
        }));
        
      } catch (error) {
        console.error("Error fetching dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (isLoading || !stats) {
    return <div className="text-center p-20 animate-pulse text-textMuted font-bold">Initializing Surveillance Matrix...</div>;
  }

  const statCards = [
    { title: "Active Alerts", value: stats.active_alerts, icon: AlertTriangle, color: "text-danger" },
    { title: "Today's Triggers", value: stats.today_alerts, icon: Activity, color: "text-primary" },
    { title: "Avg Response (sec)", value: stats.avg_response_time_seconds, icon: Clock, color: "text-success" },
    { title: "Active Users", value: stats.total_users, icon: Users, color: "text-[#38BDF8]" }
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Command Center</h2>
          <p className="text-textMuted">Live view of active emergency infrastructure</p>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 glass-panel border border-primary/30 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
            <span className="text-sm font-bold text-success truncate">Systems Operational</span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="glass-panel p-6 relative overflow-hidden group">
              <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 group-hover:opacity-10 transition-all duration-500">
                <Icon size={120} />
              </div>
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-sm font-medium text-textMuted">{card.title}</h3>
                <Icon className={card.color} size={20} />
              </div>
              <p className="text-3xl font-bold text-white">{card.value}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Analytics Chart */}
        <div className="lg:col-span-2 glass-panel p-6">
          <h3 className="text-lg font-bold text-white mb-6">7-Day Alert Trajectory</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#F8FAFC' }}
                />
                <Area type="monotone" dataKey="alerts" stroke="#7C3AED" strokeWidth={3} fillOpacity={1} fill="url(#colorAlerts)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Incidence Feed */}
        <div className="lg:col-span-1 glass-panel p-6 flex flex-col h-full max-h-[400px]">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center justify-between">
            Recent Incidents
            <ShieldAlert size={18} className="text-danger" />
          </h3>
          <div className="overflow-y-auto pr-2 space-y-4 flex-1">
            {incidents.length === 0 ? (
              <p className="text-textMuted text-sm text-center italic py-4">No recent tracking logs found.</p>
            ) : (
              incidents.map((incident) => (
                <div key={incident.id} className="p-4 bg-darker/50 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-primary">
                      {incident.incident_type}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full capitalize ${incident.status === 'open' ? 'bg-danger/20 text-danger' : 'bg-success/20 text-success'}`}>
                      {incident.status}
                    </span>
                  </div>
                  <p className="text-sm text-white font-medium mb-1 truncate">{incident.user_name}</p>
                  <p className="text-xs text-textMuted truncate">{incident.location.address}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Admin User Tracking Directory Grid */}
      <div className="glass-panel p-6 mt-8">
        <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Users size={18} className="text-primary" />
          Physical Node Directory
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-textMuted">
            <thead className="bg-black/20 text-xs uppercase font-medium text-white/50 border-b border-white/10">
              <tr>
                <th className="px-4 py-3">Node Name</th>
                <th className="px-4 py-3">Contact Email</th>
                <th className="px-4 py-3">Hardware ID</th>
                <th className="px-4 py-3 text-center">Auth Role</th>
                <th className="px-4 py-3 text-right">Lifetime Triggers</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {usersGrid.map(usr => (
                <tr key={usr.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-white font-medium">{usr.name}</td>
                  <td className="px-4 py-3 font-mono text-xs">{usr.email}</td>
                  <td className="px-4 py-3">{usr.phone}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider ${usr.role === 'admin' ? 'bg-danger/20 text-danger border border-danger/20' : 'bg-primary/20 text-primary border border-primary/20'}`}>
                      {usr.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-white font-bold">{usr.total_alerts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
