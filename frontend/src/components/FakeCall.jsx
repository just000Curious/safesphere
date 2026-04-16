import React, { useState, useEffect } from 'react';
import { Phone, X, Plus } from 'lucide-react';

export default function FakeCall({ onDismiss }) {
  const [callState, setCallState] = useState('incoming'); // incoming, active
  const [duration, setDuration] = useState(0);

  // Play ringing sound natively looping HTML5 Audio Context
  useEffect(() => {
    let audioCtx_local;
    let oscillator;
    let interval;

    if (callState === 'incoming') {
      try {
        audioCtx_local = new (window.AudioContext || window.webkitAudioContext)();
        
        const playRing = () => {
          if (!audioCtx_local) return;
          oscillator = audioCtx_local.createOscillator();
          const gainNode = audioCtx_local.createGain();
          
          oscillator.type = 'sine';
          oscillator.frequency.setValueAtTime(440, audioCtx_local.currentTime); // 440 Hz
          oscillator.frequency.setValueAtTime(480, audioCtx_local.currentTime + 0.5); // Alternative UK/EU ring
          
          gainNode.gain.setValueAtTime(0, audioCtx_local.currentTime);
          gainNode.gain.linearRampToValueAtTime(0.5, audioCtx_local.currentTime + 0.1);
          gainNode.gain.linearRampToValueAtTime(0, audioCtx_local.currentTime + 1.5);
          
          oscillator.connect(gainNode);
          gainNode.connect(audioCtx_local.destination);
          
          oscillator.start(audioCtx_local.currentTime);
          oscillator.stop(audioCtx_local.currentTime + 1.5);
        };
        
        playRing();
        interval = setInterval(playRing, 3000);
      } catch (e) {
        console.warn("AudioContext blocked by browser policy until interaction");
      }
    } else if (callState === 'active') {
      interval = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    }

    return () => {
      clearInterval(interval);
      if (oscillator) {
        try { oscillator.stop(); } catch(e) {}
      }
      if (audioCtx_local && audioCtx_local.state !== 'closed') {
        audioCtx_local.close();
      }
    };
  }, [callState]);

  const handleAccept = () => setCallState('active');
  const handleDecline = () => onDismiss();

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="fixed inset-0 z-[100] grid place-items-center bg-black/90 backdrop-blur-xl">
      <div className="w-full h-full sm:h-auto sm:max-w-md sm:aspect-[9/19] sm:rounded-[3rem] bg-slate-900 border-[8px] sm:border-[12px] border-black flex flex-col items-center justify-between py-16 px-6 shadow-2xl relative overflow-hidden">
        
        {/* Dynamic Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-indigo-900/50 to-transparent"></div>

        <div className="text-center z-10 w-full mt-8">
          <p className="text-xl font-medium text-white/50 mb-2 tracking-widest uppercase">SafeSphere Secure Line</p>
          <h1 className="text-5xl font-normal text-white mb-4">Command Center</h1>
          {callState === 'incoming' ? (
            <p className="text-white/80 animate-pulse text-lg">Calling mobile...</p>
          ) : (
            <p className="text-success text-2xl font-mono tracking-wider">{formatTime(duration)}</p>
          )}
        </div>

        {callState === 'incoming' ? (
          <div className="w-full flex justify-between px-12 pb-12 z-10">
            <button 
              onClick={handleDecline}
              className="w-[72px] h-[72px] rounded-full bg-danger flex items-center justify-center animate-bounce hover:bg-danger/80"
            >
              <Phone className="text-white rotate-[135deg]" size={36} />
            </button>
            <button 
              onClick={handleAccept}
              className="w-[72px] h-[72px] rounded-full bg-success flex items-center justify-center animate-bounce hover:bg-success/80 ring-8 ring-success/20"
              style={{ animationDelay: '0.2s' }}
            >
              <Phone className="text-white fill-white" size={36} />
            </button>
          </div>
        ) : (
          <div className="w-full z-10 space-y-12 pb-8">
             <div className="grid grid-cols-3 gap-y-8 px-6">
                {/* Mock native iOS/Android call controls */}
                <div className="flex flex-col items-center gap-2 opacity-70"><div className="w-8 h-8 rounded bg-white/20"></div><span className="text-white/60 text-xs">mute</span></div>
                <div className="flex flex-col items-center gap-2 opacity-70"><div className="w-8 h-8 rounded bg-white/20"></div><span className="text-white/60 text-xs">keypad</span></div>
                <div className="flex flex-col items-center gap-2 opacity-70"><div className="w-8 h-8 rounded bg-white/20"></div><span className="text-white/60 text-xs">speaker</span></div>
             </div>
             
             <div className="flex justify-center">
              <button 
                onClick={handleDecline}
                className="w-[72px] h-[72px] rounded-full bg-danger flex items-center justify-center hover:bg-danger/80"
              >
                <Phone className="text-white rotate-[135deg]" size={36} />
              </button>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
