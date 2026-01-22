// web/src/network.ts
/**
 * WebSocket client for connecting to the Texting of Isaac game server.
 * Handles connection, reconnection, message parsing, and input sending.
 */

/**
 * Session information received from the server after connecting.
 */
export interface SessionInfo {
    sessionId: string;
    role: 'player' | 'spectator';
    status: string;
}

/**
 * Complete game state sent from server every frame.
 */
export interface GameState {
    frame: {
        width: number;
        height: number;
    };
    entities: Array<{
        id: number;
        type: string;
        components: Record<string, any>;
    }>;
    player: {
        id: number;
        type: string;
        components: Record<string, any>;
    } | null;
    ui: {
        currency: {
            coins: number;
            bombs: number;
        };
        health: {
            current: number;
            max: number;
        };
        items: string[];
    };
    room: {
        position: [number, number] | null;
        doors: Array<{
            id: number;
            type: string;
            components: Record<string, any>;
        }>;
    };
}

/**
 * Callbacks for network events.
 */
export type NetworkEventHandler = {
    onSessionInfo?: (info: SessionInfo) => void;
    onGameState?: (state: GameState) => void;
    onDisconnect?: () => void;
    onError?: (error: string) => void;
};

/**
 * WebSocket client for game communication.
 */
export class NetworkClient {
    private ws: WebSocket | null = null;
    private handlers: NetworkEventHandler;
    private url: string;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeoutId: number | null = null;
    private role: 'player' | 'spectator' = 'player';
    private sessionId?: string;

    constructor(url: string, handlers: NetworkEventHandler) {
        this.url = url;
        this.handlers = handlers;
    }

    /**
     * Connect to the WebSocket server.
     * @param role - 'player' to start a new game, 'spectator' to watch
     * @param sessionId - Required for spectator role, optional for player
     */
    connect(role: 'player' | 'spectator', sessionId?: string): void {
        // Clear any pending reconnection attempts
        if (this.reconnectTimeoutId !== null) {
            clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }

        // Store connection parameters for reconnection
        this.role = role;
        this.sessionId = sessionId;

        // Create WebSocket connection
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            this.reconnectAttempts = 0;

            // Send connect message
            const connectMessage = {
                type: 'connect',
                role,
                ...(sessionId && { sessionId })
            };
            this.send(connectMessage);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                this.handlers.onError?.('Invalid message format');
            }
        };

        this.ws.onerror = (error) => {
            this.handlers.onError?.('Connection error');
        };

        this.ws.onclose = () => {
            this.handlers.onDisconnect?.();
            this.attemptReconnect();
        };
    }

    /**
     * Handle incoming messages from the server.
     */
    private handleMessage(data: any): void {
        if (data.type === 'session_info') {
            // Session info from backend (initial handshake)
            const info: SessionInfo = {
                sessionId: data.sessionId,
                role: data.role,
                status: data.status
            };
            this.handlers.onSessionInfo?.(info);
        } else if (data.type === 'error') {
            this.handlers.onError?.(data.message);
        } else if (data.frame && data.entities) {
            // Game state update (has frame and entities fields)
            this.handlers.onGameState?.(data as GameState);
        }
    }

    /**
     * Send player input to the server.
     * Only valid for player connections.
     * @param key - Key that was pressed/released (e.g., 'w', 'ArrowUp')
     * @param action - 'press' or 'release'
     */
    sendInput(key: string, action: 'press' | 'release' = 'press'): void {
        // Only allow players to send input, silently ignore for spectators
        if (this.role !== 'player') {
            return;
        }

        const inputMessage = {
            type: 'input',
            key,
            action
        };
        this.send(inputMessage);
    }

    /**
     * Send a message to the server.
     */
    private send(message: any): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    /**
     * Calculate reconnection delay with exponential backoff.
     * Starts at 2000ms and increases by 1.5x each attempt, capped at 10000ms.
     */
    private getReconnectDelay(): number {
        return Math.min(2000 * Math.pow(1.5, this.reconnectAttempts), 10000);
    }

    /**
     * Attempt to reconnect to the server.
     */
    private attemptReconnect(): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.getReconnectDelay();
            this.reconnectTimeoutId = window.setTimeout(() => {
                this.connect(this.role, this.sessionId);
            }, delay);
        } else {
            this.handlers.onError?.('Failed to reconnect after multiple attempts');
        }
    }

    /**
     * Disconnect from the server.
     */
    disconnect(): void {
        // Clear any pending reconnection attempts
        if (this.reconnectTimeoutId !== null) {
            clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }

        // Close WebSocket connection
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        // Reset reconnection counter
        this.reconnectAttempts = 0;
    }

}
