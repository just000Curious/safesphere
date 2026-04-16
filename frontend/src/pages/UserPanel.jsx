import React, { useState, useEffect, useRef, useContext } from 'react';
import SOSTrigger from '../components/SOSTrigger';
import MapDashboard from '../components/MapDashboard';
import FakeCall from '../components/FakeCall';
import api from '../api';
import { AuthContext } from '../context/AuthContext';
import { ToastContext } from '../context/ToastContext';
import { Phone, Clock, PlaySquare, XSquare } from 'lucide-react';

export default function UserPanel() {
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [systemStatus, setSystemStatus] = useState('Connecting...');
  const [wsKey, setWsKey] = useState(Date.now());
  const [userLocation, setUserLocation] = useState([28.6139, 77.2090]); // Default origin
  const [showFakeCall, setShowFakeCall] = useState(false);
  const [timerStatus, setTimerStatus] = useState(null); // null, active
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [activeTimerInput, setActiveTimerInput] = useState(15);
  
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const { user } = useContext(AuthContext);
  const { showToast } = useContext(ToastContext);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserLocation([pos.coords.latitude, pos.coords.longitude]),
        (err) => console.log("Geolocator prompt blocked/failed", err)
      );
    }
    const ws = new WebSocket(`ws://localhost:8000/ws/track/${user?.id || "anonymous"}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setSystemStatus('Online');
      console.log('Connected to SafeSphere Live Engine');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'location_update') {
          setActiveAlerts(prev => [...prev, message.location]);
        }
      } catch (err) { }
    };

    ws.onclose = () => {
      setSystemStatus('Offline');
      setTimeout(() => setWsKey(Date.now()), 5000); 
    };

    return () => ws.close();
  }, [wsKey, user?.id]);

  useEffect(() => {
    let interval = null;
    if (timerStatus === 'active' && timerSeconds > 0) {
      interval = setInterval(() => setTimerSeconds(prev => prev - 1), 1000);
    } else if (timerStatus === 'active' && timerSeconds <= 0) {
      clearInterval(interval);
      setTimerStatus(null);
      // Dead Man Switch execution!
      showToast('Dead Man Switch Triggered!', 'error');
      handleSOS('timer', 'start');
    }
    return () => clearInterval(interval);
  }, [timerStatus, timerSeconds]);

  const startTimer = () => {
    setTimerSeconds(activeTimerInput * 60);
    setTimerStatus('active');
    showToast(`Safety Timer set for ${activeTimerInput} minutes.`, 'success');
  };
  
  const cancelTimer = () => {
    setTimerStatus(null);
    showToast('Timer disarmed.', 'warning');
  };

  const [currentAlertId, setCurrentAlertId] = useState(null);

  // Blackbox Microphone Interceptor
  const startBlackbox = async (alertId) => {
    try {
      showToast('Blackbox Audio Evidence Recording...', 'warning');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'evidence.webm');
        try {
          await api.post(`/alerts/${alertId}/audio`, formData, { headers: { 'Content-Type': 'multipart/form-data'}});
          showToast('Evidence Secured & Synced.', 'success');
        } catch(e) {
          showToast('Failed to sync audio.', 'error');
        }
        stream.getTracks().forEach(track => track.stop());
      };

      // Spans entire SOS duration physically capturing ambient noise logically
      mediaRecorder.start();
    } catch (err) {
      showToast('Microphone access blocked. Blackbox disabled.', 'error');
    }
  };

  const handleSOS = async (method, action) => {
    const mockLat = userLocation[0] || 28.6139;
    const mockLng = userLocation[1] || 77.2090;

    if (action === 'start') {
      try {
        const response = await api.post("/alerts/trigger", {
          severity: "critical", // Upgraded to critical immediately on dynamic triggers
          latitude: mockLat,
          longitude: mockLng,
          address: "123 Emergency UI Lane"
        });
        
        setCurrentAlertId(response.data.id);
        const newAlert = { id: response.data.id, latitude: mockLat, longitude: mockLng, method };
        setActiveAlerts(prev => [...prev, newAlert]);
        
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: "location_update", user_id: user?.id || "anonymous", location: { latitude: mockLat, longitude: mockLng, speed: 0 } }));
        }

        // Engage Blackbox physically natively
        startBlackbox(response.data.id);
        
      } catch (error) {
        showToast('SOS API Error.', 'error');
      }
    } else if (action === 'stop' && currentAlertId) {
      try {
        // Stop audio recording explicitly capturing the final blob to send
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
           mediaRecorderRef.current.stop();
        }

        await api.put(`/alerts/${currentAlertId}/resolve`);
        setCurrentAlertId(null);
        setActiveAlerts(prev => prev.filter(alert => alert.id !== currentAlertId));
        showToast('Alarm Terminated Safely.', 'success');
      } catch (error) {
        showToast('Alarm Termination Error', 'error');
      }
    }
  };

  const formatSecs = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
        <div className="lg:col-span-1 space-y-6">
          <SOSTrigger onTrigger={handleSOS} />
          
          {/* Tactical Defender Controls */}
          <div className="glass-panel p-6 border-warning/20">
            <h3 className="font-bold text-white mb-4">Tactical Deterrence</h3>
            <div className="space-y-4">
              <button 
                onClick={() => setShowFakeCall(true)}
                className="w-full flex items-center justify-between p-3 rounded-lg bg-black/20 hover:bg-black/40 border border-white/5 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-primary/20 text-primary group-hover:scale-110 transition-transform"><Phone size={18} /></div>
                  <div className="text-left"><p className="text-sm font-bold text-white">Fake Call Override</p><p className="text-xs text-textMuted">Simulate incoming ring</p></div>
                </div>
              </button>

              <div className="p-3 rounded-lg bg-black/20 border border-white/5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-full bg-warning/20 text-warning"><Clock size={18} /></div>
                  <div className="text-left"><p className="text-sm font-bold text-white">Dead Man's Switch</p><p className="text-xs text-textMuted">Auto-trigger if unconcealed</p></div>
                </div>
                {timerStatus === 'active' ? (
                  <div className="flex items-center justify-between bg-darker p-2 rounded-md">
                    <span className="text-success font-mono font-bold tracking-widest text-lg ml-2 animate-pulse">{formatSecs(timerSeconds)}</span>
                    <button onClick={cancelTimer} className="px-3 py-1 bg-danger/20 text-danger rounded hover:bg-danger text-sm font-bold flex items-center gap-1 transition-colors"><XSquare size={14}/> Disarm</button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <input type="number" min="1" max="60" value={activeTimerInput} onChange={e => setActiveTimerInput(e.target.value)} className="w-16 bg-darker border border-white/10 rounded px-2 py-1 text-sm text-center font-bold text-white outline-none focus:border-primary" />
                    <span className="text-xs text-textMuted self-center">min</span>
                    <button onClick={startTimer} className="flex-1 bg-warning/20 hover:bg-warning/40 text-warning rounded py-1 text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-2"><PlaySquare size={14} /> Arm Switch</button>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="glass-panel p-6">
            <h3 className="font-bold text-white mb-4">Live Proximity</h3>
            <div className="space-y-4 text-sm font-medium">
              <div className="flex justify-between items-center pb-2 border-b border-white/5">
                <span className="text-textMuted text-sm">System Status</span>
                <span className={`text-sm font-bold flex items-center gap-2 ${systemStatus === 'Online' ? 'text-success' : 'text-danger'}`}>
                  <span className={`w-2 h-2 rounded-full ${systemStatus === 'Online' ? 'bg-success animate-pulse' : 'bg-danger'}`}></span>
                  {systemStatus}
                </span>
             </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 flex flex-col min-h-[500px]">
          <MapDashboard activeAlerts={activeAlerts} />
        </div>
      </div>
      
      {showFakeCall && <FakeCall onDismiss={() => setShowFakeCall(false)} />}
    </>
  );
}
