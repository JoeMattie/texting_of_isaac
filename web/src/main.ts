// web/src/main.ts

import './ui/styles.css';
import * as PIXI from 'pixi.js';
import { NetworkClient, GameState } from './network';
import { SpriteManager } from './sprites';
import { GameRenderer, SHAKE_CONFIG } from './renderer';
import { UIManager } from './ui';
import { AnimationManager, EntityType } from './animations';
import { InterpolationManager } from './interpolation';
import { ParticleManager } from './particles';
import { TransitionManager } from './transitions';
import { DamageNumberManager } from './damageNumbers';
import { GameOverlay } from './ui/GameOverlay';
import { Minimap } from './ui/Minimap';

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

    // Create game container for all game content (allows transition effects)
    const gameContainer = new PIXI.Container();
    app.stage.addChild(gameContainer);

    // Initialize renderer (uses gameContainer for transitions)
    const renderer = new GameRenderer(app, spriteManager, gameContainer);

    // Initialize animation manager
    const animationManager = new AnimationManager();

    // Initialize interpolation manager
    const interpolationManager = new InterpolationManager();

    // Initialize particle manager (inside game container)
    const particleContainer = new PIXI.Container();
    gameContainer.addChild(particleContainer);
    const particleManager = new ParticleManager(particleContainer);

    // Initialize damage number manager (above particles, but inside game container)
    const damageContainer = new PIXI.Container();
    gameContainer.addChild(damageContainer);
    const damageNumbers = new DamageNumberManager(damageContainer);

    // Initialize transition manager for room transitions
    const transitionManager = new TransitionManager(1920, 640);

    // Full-screen black overlay for fade-to-black during room transitions
    const fadeOverlay = new PIXI.Graphics();
    fadeOverlay.rect(0, 0, 1920, 640).fill({ color: 0x000000 });
    fadeOverlay.alpha = 0;
    app.stage.addChild(fadeOverlay); // Above gameContainer so it covers everything

    // Track previous state for change detection
    let previousState: GameState | null = null;

    // Track previous room position for transition detection
    let previousRoomPosition: [number, number] | null = null;

    // Track session info for spectator overlay
    let currentSessionId: string = '';
    let gameStartTime: number = Date.now();

    // Connect to game server
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';
    let networkClient: NetworkClient;

    // Initialize UI manager with callbacks
    const uiManager = new UIManager(document.body, {
        onPlay: () => {
            networkClient.connect('player');
            uiManager.showGame(false);
            gameOverlay.hide();
        },
        onSpectate: () => {
            networkClient.fetchSessionList();
        },
        onJoinSession: (sessionId: string) => {
            networkClient.connect('spectator', sessionId);
            uiManager.showGame(true);
            gameOverlay.hide();
        }
    });

    // Initialize game overlay for death/victory screens
    const gameOverlay = new GameOverlay(document.body, {
        onRestart: () => {
            networkClient.disconnect();
            networkClient.connect('player');
            gameOverlay.hide();
        },
        onMainMenu: () => {
            networkClient.disconnect();
            uiManager.showLandingPage();
            gameOverlay.hide();
            minimap.hide();
        }
    });

    // Initialize minimap
    const minimap = new Minimap(document.body);

    networkClient = new NetworkClient(wsUrl, {
        onSessionInfo: (info) => {
            console.log('Session established:', info);
            currentSessionId = info.sessionId;
            gameStartTime = Date.now();
            uiManager.updateSessionInfo(info);
            uiManager.showGame(info.role === 'spectator');
        },
        onGameState: (state: GameState) => {
            // Detect room transition
            const currentRoomPosition = state.session?.roomPosition;
            if (previousRoomPosition && currentRoomPosition) {
                if (previousRoomPosition[0] !== currentRoomPosition[0] ||
                    previousRoomPosition[1] !== currentRoomPosition[1]) {
                    // Room transition detected – trigger slide + fade effect
                    transitionManager.startTransition(previousRoomPosition, currentRoomPosition);
                    // Clear interpolation targets for smooth new room entry
                    interpolationManager.clear();
                }
            }
            previousRoomPosition = currentRoomPosition ?? null;

            // Update interpolation targets
            for (const entity of state.entities) {
                if (entity.components.position) {
                    const pixelX = entity.components.position.x * 32; // tileSize
                    const pixelY = entity.components.position.y * 32;
                    interpolationManager.setTarget(entity.id, pixelX, pixelY);
                }
            }

            // Detect state changes for triggered animations
            if (previousState) {
                detectStateChanges(
                    previousState,
                    state,
                    animationManager,
                    interpolationManager,
                    particleManager,
                    transitionManager,
                    damageNumbers,
                    uiManager,
                );
            }
            previousState = state;

            // Check for game end state and show overlay
            const gameState = state.session?.gameState;
            if (gameState === 'victory' || gameState === 'game_over') {
                if (!gameOverlay.isVisible()) {
                    gameOverlay.show(gameState, {
                        floor: state.session?.floor,
                        items: state.ui?.items
                    });
                }
            } else if (gameOverlay.isVisible()) {
                gameOverlay.hide();
            }

            // Render game state (creates sprites)
            renderer.render(state);

            // Apply animations after render
            applyAnimations(renderer, state, animationManager);

            // Update UI
            if (state.ui) {
                uiManager.updateHUD({
                    health: state.ui.health,
                    coins: state.ui.currency.coins,
                    bombs: state.ui.currency.bombs,
                    items: state.ui.items,
                    floor: state.session?.floor ?? 1
                });
            }

            // Update spectator overlay if applicable
            if (state.player && state.ui) {
                const timePlayed = Math.floor((Date.now() - gameStartTime) / 1000);
                uiManager.updateSpectatorOverlay({
                    sessionId: currentSessionId,
                    playerHealth: state.player.components.health?.current ?? 0,
                    floor: state.session?.floor ?? 1,
                    items: state.ui.items,
                    timePlayed,
                    spectatorCount: state.session?.spectatorCount ?? 0
                });
            }

            // Update minimap
            if (state.session?.minimap) {
                minimap.update(state.session.minimap, state.session.roomPosition);
                if (!minimap.isVisible()) {
                    minimap.show();
                }
            }
        },
        onSessionList: (sessions) => {
            uiManager.showSessionList(sessions);
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

    // Animation and interpolation update loop
    app.ticker.add((ticker) => {
        const dt = ticker.deltaMS / 1000;
        animationManager.update(dt);
        interpolationManager.update(dt);
        particleManager.update(dt);
        damageNumbers.update(dt);
        transitionManager.update(dt);

        // Apply transition offset to game container
        const offset = transitionManager.getOffset();
        gameContainer.x = offset.x;
        gameContainer.y = offset.y;

        // Update fade overlay alpha for room transitions
        fadeOverlay.alpha = transitionManager.getFadeAlpha();

        // Apply interpolated positions to sprites
        const sprites = renderer.getEntitySprites();
        for (const [entityId, sprite] of sprites) {
            const pos = interpolationManager.getPosition(entityId);
            if (pos) {
                sprite.x = pos.currentX;
                sprite.y = pos.currentY;
            }
        }

        // Spawn trails for projectiles (only when not transitioning)
        if (previousState && !transitionManager.isTransitioning()) {
            for (const entity of previousState.entities) {
                if (entity.type === 'projectile' || entity.type === 'enemy_projectile') {
                    const pos = interpolationManager.getPosition(entity.id);
                    if (pos) {
                        particleManager.spawnTrail(pos.currentX, pos.currentY, entity.type);
                    }
                }
            }
        }
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
 */
function detectStateChanges(
    prev: GameState,
    curr: GameState,
    animationManager: AnimationManager,
    interpolationManager: InterpolationManager,
    particleManager: ParticleManager,
    transitionManager: TransitionManager,
    damageNumbers: DamageNumberManager,
    uiManager: UIManager,
): void {
    // Detect player hit
    if (prev.player && curr.player) {
        const prevHealth = prev.player.components.health?.current;
        const currHealth = curr.player.components.health?.current;
        if (prevHealth !== undefined && currHealth !== undefined && currHealth < prevHealth) {
            const damageTaken = prevHealth - currHealth;
            animationManager.triggerFlash(curr.player.id);
            // Medium screen shake on player damage
            transitionManager.startShake(SHAKE_CONFIG.medium.intensity, SHAKE_CONFIG.medium.duration);
            // Spawn hit sparks on the player
            const playerPos = interpolationManager.getPosition(curr.player.id);
            if (playerPos) {
                particleManager.spawnHitSpark(playerPos.currentX, playerPos.currentY, 'enemy_projectile');
                damageNumbers.add(playerPos.currentX, playerPos.currentY - 16, damageTaken, 'player');
            }
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
                    const damageTaken = prevHealth - currHealth;
                    animationManager.triggerFlash(currEntity.id);

                    // Heavy shake for tank (boss-tier), light for others
                    const isTank = currEntity.type === 'enemy_tank';
                    transitionManager.startShake(
                        isTank ? SHAKE_CONFIG.heavy.intensity : SHAKE_CONFIG.light.intensity,
                        isTank ? SHAKE_CONFIG.heavy.duration  : SHAKE_CONFIG.light.duration,
                    );

                    const enemyPos = interpolationManager.getPosition(currEntity.id);
                    if (enemyPos) {
                        particleManager.spawnHitSpark(enemyPos.currentX, enemyPos.currentY, currEntity.type);
                        damageNumbers.add(enemyPos.currentX, enemyPos.currentY - 16, damageTaken, 'enemy');
                    }
                }
            }
        }
    }

    // Detect room cleared (doors unlock)
    const prevEnemies = prev.entities.filter(e => e.type.startsWith('enemy_')).length;
    const currEnemies = curr.entities.filter(e => e.type.startsWith('enemy_')).length;

    if (prevEnemies > 0 && currEnemies === 0) {
        // Room just cleared – shimmer all doors
        for (const entity of curr.entities) {
            if (entity.type === 'door') {
                const pos = interpolationManager.getPosition(entity.id);
                if (pos) {
                    particleManager.spawnShimmer(pos.currentX, pos.currentY);
                }
            }
        }
    }

    // Detect deaths and spawn effects
    const currIds = new Set(curr.entities.map(e => e.id));
    for (const prevEntity of prev.entities) {
        if (!currIds.has(prevEntity.id)) {
            const pos = interpolationManager.getPosition(prevEntity.id);

            // Enemy death = explosion burst
            if (prevEntity.type.startsWith('enemy_') && pos) {
                particleManager.spawnExplosion(pos.currentX, pos.currentY, prevEntity.type);
            }

            // Heart pickup
            if (prevEntity.type === 'heart' && pos) {
                particleManager.spawnHeartPickup(pos.currentX, pos.currentY);
            }

            // Coin pickup
            if (prevEntity.type === 'coin' && pos) {
                particleManager.spawnCoinPickup(pos.currentX, pos.currentY);
            }

            // Bomb or generic item pickup
            if ((prevEntity.type === 'bomb' || prevEntity.type === 'item') && pos) {
                particleManager.spawnSparkle(pos.currentX, pos.currentY);
            }

            // Cleanup
            animationManager.removeEntity(prevEntity.id);
            interpolationManager.removeEntity(prevEntity.id);
        }
    }
}

/**
 * Apply animation transforms to entity sprites.
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
