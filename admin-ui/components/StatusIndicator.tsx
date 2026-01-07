'use client';

import React, { useEffect, useState } from 'react';

export default function StatusIndicator() {
  const [dbStatus, setDbStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkDatabaseStatus = async () => {
    try {
      setDbStatus('checking');
      const response = await fetch('http://localhost:8000/api/admin/status/database', {
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
                      dbStatus === 'disconnected' ? 'bg-red-100 border-red-300' : 
                      'bg-yellow-100 border-yellow-300';
  
  const statusDotColor = dbStatus === 'connected' ? 'bg-green-500' : 
                         dbStatus === 'disconnected' ? 'bg-red-500' : 
                         'bg-yellow-500';
  
  const statusText = dbStatus === 'connected' ? 'Database Connected' : 
                     dbStatus === 'disconnected' ? 'Database Disconnected' : 
                     'Checking...';

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
