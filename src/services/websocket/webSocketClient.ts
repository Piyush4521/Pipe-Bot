import { APP_CONFIG } from '@/constants/config';
import type { ConnectionState } from '@/types';

// Proposed WebSocket Message Envelope Contracts
export type WebSocketMessageType =
  | 'system_status'
  | 'telemetry_encoder'
  | 'telemetry_imu'
  | 'vehicle_status'
  | 'inspection_status'
  | 'defect_detected'
  | 'connection_error';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType;
  timestamp: string;
  payload: T;
}

export type MessageHandler = (message: WebSocketMessage) => void;
export type StateChangeHandler = (state: ConnectionState) => void;

export class WebSocketClient {
  private socket: WebSocket | null = null;
  private state: ConnectionState = 'disconnected';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private messageListeners: Set<MessageHandler> = new Set();
  private stateListeners: Set<StateChangeHandler> = new Set();
  private explicitDisconnect = false;
  private url: string;

  constructor(url: string = APP_CONFIG.wsUrl) {
    this.url = url;
  }

  public getState(): ConnectionState {
    return this.state;
  }

  private setState(newState: ConnectionState) {
    if (this.state !== newState) {
      this.state = newState;
      this.stateListeners.forEach((listener) => listener(newState));
    }
  }

  public connect(): void {
    if (!this.url || this.url.trim() === '') {
      this.setState('disconnected');
      return;
    }

    if (typeof window === 'undefined' || typeof WebSocket === 'undefined') {
      this.setState('disconnected');
      return;
    }

    // Validate protocol
    if (!this.url.startsWith('ws://') && !this.url.startsWith('wss://')) {
      this.setState('disconnected');
      return;
    }

    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return; // Prevent duplicate connections
    }

    this.explicitDisconnect = false;
    this.setState('connecting');

    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.setState('connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as WebSocketMessage;
          if (parsed && parsed.type) {
            this.messageListeners.forEach((listener) => listener(parsed));
          }
        } catch {
          // Discard malformed packets safely without throwing
        }
      };

      this.socket.onerror = () => {
        this.setState('error');
      };

      this.socket.onclose = () => {
        if (!this.explicitDisconnect) {
          this.handleReconnect();
        } else {
          this.setState('disconnected');
        }
      };
    } catch {
      this.setState('error');
      this.handleReconnect();
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setState('disconnected');
      return;
    }

    this.setState('reconnecting');
    this.reconnectAttempts++;
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s
    const backoffMs = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 16000);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, backoffMs);
  }

  public disconnect(): void {
    this.explicitDisconnect = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.setState('disconnected');
  }

  public subscribe(handler: MessageHandler): () => void {
    this.messageListeners.add(handler);
    return () => {
      this.messageListeners.delete(handler);
    };
  }

  public onStateChange(handler: StateChangeHandler): () => void {
    this.stateListeners.add(handler);
    handler(this.state);
    return () => {
      this.stateListeners.delete(handler);
    };
  }
}

// Global singleton instance (dormant until explicitly engaged)
export const globalWebSocket = new WebSocketClient();
