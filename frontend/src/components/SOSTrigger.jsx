import React, { useState, useEffect } from 'react';
import { AlertCircle, Mic, MicOff, PhoneCall, XOctagon } from 'lucide-react';

export default function SOSTrigger({ onTrigger }) {
  const [isListening, setIsListening] = useState(false);
  const [triggerState, setTriggerState] = useState('idle'); // idle, active

  // Mock voice trigger using Web Speech API
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window)) return;
    
    // eslint-disable-next-line no-undef
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('');

      if (transcript.toLowerCase().includes('help me') || transcript.toLowerCase().includes('emergency')) {
        handleToggle('voice');
      }
    };

    if (isListening) {
      recognition.start();
    } else {
      recognition.stop();
    }

    return () => recognition.stop();
  }, [isListening]);

  const handleToggle = (method = 'manual') => {
    if (triggerState === 'idle') {
      setTriggerState('active');
      if (onTrigger) onTrigger(method, 'start');
    } else {
      setTriggerState('idle');
      if (onTrigger) onTrigger(method, 'stop');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-8 glass-panel">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-textLight">Emergency SOS</h2>
        <p className="text-textMuted text-sm">Press the button or say "Help Me"</p>
      </div>

      <button
        onClick={() => handleToggle('manual')}
        className={`relative flex items-center justify-center w-48 h-48 rounded-full shadow-2xl transition-all duration-300 ${
          triggerState === 'active' 
            ? 'bg-warning animate-pulse ring-8 ring-orange-500/30' 
            : 'bg-danger hover:bg-danger/90 hover:scale-105 ring-4 ring-danger/20'
        }`}
      >
        <span className="absolute inset-0 rounded-full animate-ping opacity-20 bg-white"></span>
        <div className="flex flex-col items-center">
          {triggerState === 'idle' ? (
            <>
              <AlertCircle size={48} className="text-white mb-2" />
              <span className="text-white font-bold text-xl uppercase tracking-widest">SOS</span>
            </>
          ) : (
            <>
              <XOctagon size={48} className="text-white mb-2" />
              <span className="text-white font-bold text-lg uppercase tracking-widest">Cancel Alarm</span>
            </>
          )}
        </div>
      </button>

      <div className="flex gap-4">
        <button 
          onClick={() => setIsListening(!isListening)}
          className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium transition-colors ${
            isListening ? 'bg-danger/20 text-danger border border-danger/50' : 'bg-darker text-textMuted border border-white/10 hover:bg-white/5'
          }`}
        >
          {isListening ? <Mic size={18} /> : <MicOff size={18} />}
          {isListening ? 'Listening...' : 'Enable Voice'}
        </button>

        <button 
          onClick={() => console.log('Mocking auto-call to primary contact...')}
          className="flex items-center gap-2 px-4 py-2 rounded-full font-medium bg-darker text-textLight border border-white/10 hover:bg-white/5 transition-colors"
        >
          <PhoneCall size={18} className="text-success" />
          Auto-Call
        </button>
      </div>
    </div>
  );
}
