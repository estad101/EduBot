'use client';

import React, { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function StatusIndicator() {
  const [dbStatus, setDbStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkDatabaseStatus = async () => {
    try {
      setDbStatus('checking');
      const response = await fetch(`${API_URL}/api/admin/status/database`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.status === 'success' && data.database === 'connected') {
        setDbStatus('connected');
      } else {
        setDbStatus('disconnected');
      }
      setLastChecked(new Date());
    } catch (error) {
      console.error('Error checking database status:', error);
      setDbStatus('disconnected');
      setLastChecked(new Date());
    }
  };

  // Check database status on mount and every 30 seconds
  useEffect(() => {
    checkDatabaseStatus();
    const interval = setInterval(checkDatabaseStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = dbStatus === 'connected' ? 'bg-green-100 border-green-300' : 
                      'bg-red-100 border-red-300';
  
  const statusDotColor = dbStatus === 'connected' ? 'bg-green-500' : 
                         'bg-red-500';
  
  const statusText = dbStatus === 'connected' ? 'Database Connected' : 
                     'Database Disconnected';

  return (
    <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${statusColor} cursor-pointer hover:opacity-80 transition-opacity`}
         onClick={checkDatabaseStatus}
         title={`Last checked: ${lastChecked?.toLocaleTimeString() || 'Never'}`}>
      <div className={`w-2 h-2 rounded-full ${statusDotColor} ${dbStatus === 'checking' ? 'animate-pulse' : ''}`}></div>
      <span className="text-sm font-medium text-gray-700">{statusText}</span>
      <i className="fas fa-database text-sm text-gray-500 ml-1"></i>
    </div>
  );
}
