'use client';

import React, { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function WhatsAppIndicator() {
  const [waStatus, setWaStatus] = useState<'connected' | 'configured' | 'disconnected' | 'checking'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [phoneNumber, setPhoneNumber] = useState<string>('');

  const checkWhatsAppStatus = async () => {
    try {
      setWaStatus('checking');
      const response = await fetch(`${API_URL}/api/admin/status/whatsapp`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.status === 'success' && data.whatsapp === 'connected') {
        setWaStatus('connected');
        setPhoneNumber(data.phone_number || '');
      } else if (data.whatsapp === 'configured' || data.whatsapp === 'timeout') {
        // Token is configured but verification failed (might be invalid token or network issue)
        setWaStatus('configured');
        setPhoneNumber(data.phone_number || '');
      } else {
        // Show as 'configured' even when disconnected (ready to be configured)
        setWaStatus('configured');
      }
      setLastChecked(new Date());
    } catch (error) {
      console.error('Error checking WhatsApp status:', error);
      setWaStatus('disconnected');
      setLastChecked(new Date());
    }
  };

  // Check WhatsApp status on mount and every 30 seconds
  useEffect(() => {
    checkWhatsAppStatus();
    const interval = setInterval(checkWhatsAppStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = waStatus === 'connected' ? 'bg-green-100 border-green-300' : 
                      waStatus === 'configured' ? 'bg-yellow-100 border-yellow-300' :
                      'bg-red-100 border-red-300';
  
  const statusDotColor = waStatus === 'connected' ? 'bg-green-500' : 
                         waStatus === 'configured' ? 'bg-yellow-500' :
                         'bg-red-500';
  
  const statusText = waStatus === 'connected' ? 'WhatsApp Connected' : 
                     waStatus === 'configured' ? 'WhatsApp Configured' :
                     'WhatsApp Disconnected';

  return (
    <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${statusColor} cursor-pointer hover:opacity-80 transition-opacity`}
         onClick={checkWhatsAppStatus}
         title={`Last checked: ${lastChecked?.toLocaleTimeString() || 'Never'}${phoneNumber ? ` | ${phoneNumber}` : ''}`}>
      <div className={`w-2 h-2 rounded-full ${statusDotColor} ${waStatus === 'checking' ? 'animate-pulse' : ''}`}></div>
      <span className="text-sm font-medium text-gray-700">{statusText}</span>
      <i className="fab fa-whatsapp text-sm text-gray-500 ml-1"></i>
    </div>
  );
}
