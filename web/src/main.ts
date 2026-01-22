// web/src/main.ts

import * as PIXI from 'pixi.js';
import { NetworkClient, GameState } from './network';
import { SpriteManager } from './sprites';
import { GameRenderer } from './renderer';
import { UIManager } from './ui';
import { AnimationManager, EntityType } from './animations';

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

    // Initialize animation manager
    const animationManager = new AnimationManager();

    // Initialize UI manager
    const uiManager = new UIManager();

    // Track previous state for change detection
    let previousState: GameState | null = null;

    // Connect to game server
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
    const networkClient = new NetworkClient(wsUrl, {
        onSessionInfo: (info) => {
            console.log('Session established:', info);
            uiManager.updateSessionInfo(info);
        },
        onGameState: (state: GameState) => {
            // Detect state changes for triggered animations
            if (previousState) {
                detectStateChanges(previousState, state, animationManager);
            }
            previousState = state;

            // Render game state
            renderer.render(state);

            // Apply animations after render
            applyAnimations(renderer, state, animationManager);

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

    // Animation update loop
    app.ticker.add((ticker) => {
        animationManager.update(ticker.deltaMS / 1000);
    });

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

/**
 * Detect state changes and trigger appropriate animations.
 * @param prev - Previous game state
 * @param curr - Current game state
 * @param animationManager - Animation manager instance
 */
function detectStateChanges(prev: GameState, curr: GameState, animationManager: AnimationManager): void {
    // Detect player hit
    if (prev.player && curr.player) {
        const prevHealth = prev.player.components.health?.current;
        const currHealth = curr.player.components.health?.current;
        if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
            animationManager.triggerFlash(curr.player.id);
        }
    }

    // Detect player shooting (new player projectiles)
    const prevPlayerProjectiles = prev.entities.filter(e => e.type === 'projectile').length;
    const currPlayerProjectiles = curr.entities.filter(e => e.type === 'projectile').length;
    if (currPlayerProjectiles > prevPlayerProjectiles && curr.player) {
        animationManager.triggerPulse(curr.player.id);
    }

    // Detect enemy hits
    for (const currEntity of curr.entities) {
        if (currEntity.type.startsWith('enemy_')) {
            const prevEntity = prev.entities.find(e => e.id === currEntity.id);
            if (prevEntity) {
                const prevHealth = prevEntity.components.health?.current;
                const currHealth = currEntity.components.health?.current;
                if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
                    animationManager.triggerFlash(currEntity.id);
                }
            }
        }
    }

    // Clean up removed entities
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            animationManager.removeEntity(prevEntity.id);
        }
    }
}

/**
 * Apply animation transforms to entity sprites.
 * @param renderer - Game renderer instance
 * @param state - Current game state
 * @param animationManager - Animation manager instance
 */
function applyAnimations(renderer: GameRenderer, state: GameState, animationManager: AnimationManager): void {
    const sprites = renderer.getEntitySprites();
    for (const [entityId, sprite] of sprites) {
        const entityType = renderer.getEntityType(entityId, state) as EntityType;
        const transforms = animationManager.getTransformsForEntity(entityId, entityType);
        sprite.pivot.y = -transforms.yOffset;
        sprite.scale.set(transforms.scale);
        sprite.rotation = transforms.rotation * (Math.PI / 180);
        sprite.alpha = transforms.alpha;
    }
}

main();
