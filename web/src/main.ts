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
    let spriteManager: SpriteManager;
    try {
        spriteManager = new SpriteManager();
        await spriteManager.load();
        console.log('Sprites loaded');
    } catch (error) {
        console.error('Failed to load sprites:', error);
        document.body.innerHTML = '<div style="color: red; padding: 20px;">Failed to load game assets. Please refresh.</div>';
        return;
    }

    // Initialize renderer
    const renderer = new GameRenderer(app, spriteManager);

    // Initialize UI manager
    const uiManager = new UIManager();

    // Connect to game server
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
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
    const gameKeys = new Set(['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'e']);

    window.addEventListener('keydown', (e) => {
        if (gameKeys.has(e.key)) {
            e.preventDefault();
            networkClient.sendInput(e.key, 'press');
        }
    });

    window.addEventListener('keyup', (e) => {
        if (gameKeys.has(e.key)) {
            e.preventDefault();
            networkClient.sendInput(e.key, 'release');
        }
    });
}

main();
