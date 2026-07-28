/**
 * Reconnecting WebSocket client for real-time progress and domain event streaming.
 */

export interface WebSocketEvent {
  event_type: string;
  message: string;
  payload: any;
}

type EventListener = (event: WebSocketEvent) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private listeners: Set<EventListener> = new Set();
  private reconnectTimer: any = null;
  private isConnected: boolean = false;

  constructor() {
    this.connect();
  }

  private connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/events`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.isConnected = true;
        console.log("[DevForge WS] Connected to backend event stream.");
      };

      this.ws.onmessage = (event) => {
        try {
          const data: WebSocketEvent = JSON.parse(event.data);
          this.notify(data);
        } catch (e) {
          console.error("[DevForge WS] Error parsing message:", e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        console.warn("[DevForge WS] Connection lost. Reconnecting in 3s...");
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.error("[DevForge WS] Error:", err);
      };
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => this.connect(), 3000);
  }

  public subscribe(listener: EventListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(event: WebSocketEvent) {
    this.listeners.forEach((fn) => fn(event));
  }
}

export const wsClient = new WebSocketClient();
