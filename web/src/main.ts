// web/src/main.ts

import * as PIXI from 'pixi.js';
import { NetworkClient, GameState } from './network';
import { SpriteManager } from './sprites';
import { GameRenderer } from './renderer';
import { UIManager } from './ui';

async function main() {
    console.log('Texting of Isaac - Web Edition');
    console.log('Pixi.js version:', PIXI.VERSION);

    // Initialize Pixi.js application
    const app = new PIXI.Application();
    await app.init({
        width: 1920,
        height: 640,
        backgroundColor: 0x000000,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
    });

    const container = document.getElementById('app');
    if (container) {
        container.appendChild(app.canvas);
    }

    // Initialize sprite manager and load sprites
    const spriteManager = new SpriteManager();
    await spriteManager.load();
    console.log('Sprites loaded');

    // Initialize renderer
    const renderer = new GameRenderer(app, spriteManager);

    // Initialize UI manager
    const uiManager = new UIManager();

    // Connect to game server
    const wsUrl = 'ws://localhost:8765';
    const networkClient = new NetworkClient(wsUrl, {
        onSessionInfo: (info) => {
            console.log('Session established:', info);
            uiManager.updateSessionInfo(info);
        },
        onGameState: (state: GameState) => {
            // Render game state
            renderer.render(state);

            // Update UI
            if (state.ui) {
                uiManager.updateUI(state.ui);
            }
        },
        onDisconnect: () => {
            console.log('Disconnected from server');
            uiManager.showDisconnected();
        },
        onError: (error) => {
            console.error('Network error:', error);
            uiManager.showError(error);
        }
    });

    // Connect as player
    networkClient.connect('player');

    // Setup keyboard input (WASD for movement, arrows for shooting)
    window.addEventListener('keydown', (e) => {
        // Only send input if we're the player
        networkClient.sendInput(e.key);
    });
}

main();
