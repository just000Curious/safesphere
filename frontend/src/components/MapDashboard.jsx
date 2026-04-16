import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet marker icon issues in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Component to dynamically fly to new alerts
function MapUpdater({ activeAlerts }) {
  const map = useMap();
  useEffect(() => {
    if (activeAlerts.length > 0) {
      const latest = activeAlerts[activeAlerts.length - 1];
      map.flyTo([latest.latitude, latest.longitude], 14);
    }
  }, [activeAlerts, map]);
  return null;
}

export default function MapDashboard({ activeAlerts = [] }) {
  const defaultCenter = [28.6139, 77.2090]; // New Delhi coordinates

  return (
    <div className="w-full h-[500px] overflow-hidden glass-panel relative border border-white/10 rounded-2xl">
      <MapContainer 
        center={defaultCenter} 
        zoom={12} 
        style={{ height: '100%', width: '100%', backgroundColor: '#0F172A' }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapUpdater activeAlerts={activeAlerts} />

        {activeAlerts.map(alert => (
          <Marker key={alert.id} position={[alert.latitude, alert.longitude]}>
            <Popup>
              <strong>Active SOS</strong><br />
              Triggered via: {alert.method || 'Manual'}<br />
              Status: Escalated
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Overlay Mock Data Data Table */}
      <div className="absolute bottom-4 left-4 right-4 bg-darker/90 backdrop-blur-md border border-white/10 rounded-xl p-4 z-[400]">
        <h4 className="text-white font-bold mb-2">Active Area Warnings</h4>
        <div className="flex gap-4 overflow-x-auto pb-2">
          <div className="min-w-[200px] bg-danger/10 border border-danger/30 rounded p-3">
            <p className="text-danger text-xs font-bold uppercase mb-1">High Risk - Connaught Place</p>
            <p className="text-textLight text-sm">{activeAlerts.length} Active SOS currently tracking.</p>
          </div>
          <div className="min-w-[200px] bg-primary/10 border border-primary/30 rounded p-3">
            <p className="text-primary text-xs font-bold uppercase mb-1">Warning - Green Park</p>
            <p className="text-textLight text-sm">Elevated risk score (85/100).</p>
          </div>
        </div>
      </div>
    </div>
  );
}
