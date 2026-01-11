/**
 * useWebSocket - React hook for WebSocket connections with auto-reconnect
 * Enables real-time updates without page reload
 */
import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  timestamp?: string;
  event?: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  debug?: boolean;
}

export function useWebSocket(
  options: UseWebSocketOptions,
  onMessage?: (data: WebSocketMessage) => void,
  onConnect?: () => void,
  onDisconnect?: () => void
) {
  const { 
    url, 
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    debug = false
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Log helper
  const log = useCallback((msg: string, data?: any) => {
    if (debug) {
      console.log(`[WebSocket] ${msg}`, data || '');
    }
  }, [debug]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('Already connected');
      return;
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}${url}`;
      
      log(`Connecting to ${wsUrl}`);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        log('✓ Connected');
        setIsConnected(true);
        reconnectCountRef.current = 0;
        onConnect?.();
        
        // Send initial ping
        sendMessage({ type: 'ping' });
        
        // Heartbeat to keep connection alive
        const heartbeatInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            sendMessage({ type: 'ping' });
          }
        }, 30000); // Every 30 seconds

        ws.onclose = () => {
          clearInterval(heartbeatInterval);
        };
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          log('Received message', data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (e) {
          log('Error parsing message', e);
        }
      };

      ws.onerror = (error) => {
        log('✗ Error', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        log('✗ Disconnected');
        setIsConnected(false);
        onDisconnect?.();
        
        // Attempt reconnect
        if (reconnectCountRef.current < maxReconnectAttempts) {
          reconnectCountRef.current++;
          log(`Reconnecting in ${reconnectInterval}ms (attempt ${reconnectCountRef.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          log('Max reconnect attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      log('Connection error', error);
      setIsConnected(false);
    }
  }, [url, reconnectInterval, maxReconnectAttempts, onMessage, onConnect, onDisconnect, log]);

  // Send message
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('Sending message', message);
      wsRef.current.send(JSON.stringify(message));
    } else {
      log('WebSocket not connected, cannot send message');
    }
  }, [log]);

  // Disconnect
  const disconnect = useCallback(() => {
    log('Disconnecting');
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, [log]);

  // Connect on mount, cleanup on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect
  };
}
