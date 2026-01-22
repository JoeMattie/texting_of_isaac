# Phase 4 UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add polished retro-game UI with HUD, landing page, and spectator mode.

**Architecture:** Modular UI components orchestrated by UIManager.

**Tech Stack:** TypeScript, HTML/CSS, Press Start 2P font

---

## Task 1: Add pixel font and base styles

**Files:**
- Modify: `web/index.html`
- Create: `web/src/ui/styles.css`

**Step 1: Add Google Font to index.html**

Add to `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
```

**Step 2: Create base styles**

Create `web/src/ui/styles.css`:
```css
/* Retro game UI styles */

:root {
  --pixel-font: 'Press Start 2P', monospace;
  --color-red: #ff0000;
  --color-gold: #ffcc00;
  --color-white: #ffffff;
  --color-gray: #666666;
  --color-dark: #111111;
  --color-bg: rgba(0, 0, 0, 0.9);
  --border-pixel: 2px solid var(--color-white);
}

.pixel-text {
  font-family: var(--pixel-font);
  image-rendering: pixelated;
}

.pixel-border {
  border: var(--border-pixel);
  box-shadow:
    inset -2px -2px 0 var(--color-gray),
    inset 2px 2px 0 var(--color-white);
}

.scanlines {
  position: relative;
}

.scanlines::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1) 0px,
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
}
```

**Step 3: Import styles in main.ts**

Add at top of main.ts:
```typescript
import './ui/styles.css';
```

**Step 4: Commit**

```bash
git add web/index.html web/src/ui/styles.css web/src/main.ts
git commit -m "feat(web): add pixel font and retro base styles"
```

---

## Task 2: Create HUD component

**Files:**
- Create: `web/src/ui/HUD.ts`
- Create: `web/src/__tests__/HUD.test.ts`

**Step 1: Write the failing test**

```typescript
// web/src/__tests__/HUD.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { HUD } from '../ui/HUD';

describe('HUD', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates HUD element', () => {
        const hud = new HUD(container);
        expect(container.querySelector('.hud')).not.toBeNull();
    });

    it('renders health hearts', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 5 }, coins: 0, bombs: 0, items: [], floor: 1 });
        const healthEl = container.querySelector('.hud-health');
        expect(healthEl?.textContent).toContain('♥♥♥');
    });

    it('renders empty hearts for missing health', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 2, max: 4 }, coins: 0, bombs: 0, items: [], floor: 1 });
        const healthEl = container.querySelector('.hud-health');
        expect(healthEl?.innerHTML).toContain('♥♥');
        expect(healthEl?.innerHTML).toContain('♡♡');
    });

    it('renders coins', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 15, bombs: 0, items: [], floor: 1 });
        const coinsEl = container.querySelector('.hud-coins');
        expect(coinsEl?.textContent).toContain('15');
    });

    it('renders bombs', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 5, items: [], floor: 1 });
        const bombsEl = container.querySelector('.hud-bombs');
        expect(bombsEl?.textContent).toContain('5');
    });

    it('renders floor number', () => {
        const hud = new HUD(container);
        hud.update({ health: { current: 3, max: 3 }, coins: 0, bombs: 0, items: [], floor: 2 });
        const floorEl = container.querySelector('.hud-floor');
        expect(floorEl?.textContent).toContain('F2');
    });

    it('destroy removes HUD', () => {
        const hud = new HUD(container);
        hud.destroy();
        expect(container.querySelector('.hud')).toBeNull();
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`

**Step 3: Write implementation**

```typescript
// web/src/ui/HUD.ts

export interface HUDData {
    health: { current: number; max: number };
    coins: number;
    bombs: number;
    items: string[];
    floor: number;
}

export class HUD {
    private container: HTMLElement;
    private element: HTMLElement;
    private healthEl: HTMLElement;
    private coinsEl: HTMLElement;
    private bombsEl: HTMLElement;
    private itemsEl: HTMLElement;
    private floorEl: HTMLElement;

    constructor(container: HTMLElement) {
        this.container = container;
        this.element = document.createElement('div');
        this.element.className = 'hud pixel-text pixel-border';
        this.element.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: var(--color-bg, rgba(0,0,0,0.9));
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 24px;
            font-size: 12px;
            z-index: 100;
        `;

        // Health
        this.healthEl = document.createElement('div');
        this.healthEl.className = 'hud-health';
        this.healthEl.style.color = 'var(--color-red, #ff0000)';
        this.element.appendChild(this.healthEl);

        // Coins
        this.coinsEl = document.createElement('div');
        this.coinsEl.className = 'hud-coins';
        this.coinsEl.style.color = 'var(--color-gold, #ffcc00)';
        this.element.appendChild(this.coinsEl);

        // Bombs
        this.bombsEl = document.createElement('div');
        this.bombsEl.className = 'hud-bombs';
        this.bombsEl.style.color = 'var(--color-white, #ffffff)';
        this.element.appendChild(this.bombsEl);

        // Items
        this.itemsEl = document.createElement('div');
        this.itemsEl.className = 'hud-items';
        this.itemsEl.style.cssText = 'flex: 1; display: flex; gap: 8px; overflow: hidden;';
        this.element.appendChild(this.itemsEl);

        // Floor
        this.floorEl = document.createElement('div');
        this.floorEl.className = 'hud-floor';
        this.floorEl.style.color = 'var(--color-white, #ffffff)';
        this.element.appendChild(this.floorEl);

        this.container.appendChild(this.element);
    }

    update(data: HUDData): void {
        // Health hearts
        const fullHearts = '<span style="color: #ff0000">♥</span>'.repeat(data.health.current);
        const emptyHearts = '<span style="color: #666666">♡</span>'.repeat(data.health.max - data.health.current);
        this.healthEl.innerHTML = fullHearts + emptyHearts;

        // Coins
        this.coinsEl.textContent = `$ ${data.coins}`;

        // Bombs
        this.bombsEl.textContent = `B ${data.bombs}`;

        // Items (show up to 6)
        const visibleItems = data.items.slice(0, 6);
        this.itemsEl.textContent = visibleItems.join(' ');

        // Floor
        this.floorEl.textContent = `F${data.floor}`;
    }

    show(): void {
        this.element.style.display = 'flex';
    }

    hide(): void {
        this.element.style.display = 'none';
    }

    destroy(): void {
        this.element.remove();
    }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`

**Step 5: Commit**

```bash
git add web/src/ui/HUD.ts web/src/__tests__/HUD.test.ts
git commit -m "feat(web): implement retro HUD component"
```

---

## Task 3: Create LandingPage component

**Files:**
- Create: `web/src/ui/LandingPage.ts`
- Create: `web/src/__tests__/LandingPage.test.ts`

**Step 1: Write the failing test**

```typescript
// web/src/__tests__/LandingPage.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { LandingPage } from '../ui/LandingPage';

describe('LandingPage', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates landing page element', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.querySelector('.landing-page')).not.toBeNull();
    });

    it('shows title', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('TEXTING OF ISAAC');
    });

    it('shows NEW GAME option', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('NEW GAME');
    });

    it('shows SPECTATE option', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        expect(container.textContent).toContain('SPECTATE');
    });

    it('calls onPlay when NEW GAME clicked', () => {
        const onPlay = vi.fn();
        const page = new LandingPage(container, { onPlay, onSpectate: () => {} });
        const newGameBtn = container.querySelector('.menu-new-game') as HTMLElement;
        newGameBtn?.click();
        expect(onPlay).toHaveBeenCalled();
    });

    it('calls onSpectate when SPECTATE clicked', () => {
        const onSpectate = vi.fn();
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate });
        const spectateBtn = container.querySelector('.menu-spectate') as HTMLElement;
        spectateBtn?.click();
        expect(onSpectate).toHaveBeenCalled();
    });

    it('shows session list', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        page.showSessionList([
            { sessionId: 'abc', playerHealth: 3, floor: 1, spectatorCount: 2 }
        ]);
        expect(container.textContent).toContain('abc');
    });

    it('destroy removes landing page', () => {
        const page = new LandingPage(container, { onPlay: () => {}, onSpectate: () => {} });
        page.destroy();
        expect(container.querySelector('.landing-page')).toBeNull();
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`

**Step 3: Write implementation**

```typescript
// web/src/ui/LandingPage.ts

export interface SessionListItem {
    sessionId: string;
    playerHealth: number;
    floor: number;
    spectatorCount: number;
}

export interface LandingPageCallbacks {
    onPlay: () => void;
    onSpectate: () => void;
    onJoinSession?: (sessionId: string) => void;
}

export class LandingPage {
    private container: HTMLElement;
    private element: HTMLElement;
    private sessionListEl: HTMLElement;
    private callbacks: LandingPageCallbacks;

    constructor(container: HTMLElement, callbacks: LandingPageCallbacks) {
        this.container = container;
        this.callbacks = callbacks;

        this.element = document.createElement('div');
        this.element.className = 'landing-page pixel-text scanlines';
        this.element.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
        `;

        // Title
        const title = document.createElement('h1');
        title.textContent = 'TEXTING OF ISAAC';
        title.style.cssText = `
            font-size: 32px;
            color: #fff;
            text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000;
            margin-bottom: 8px;
        `;
        this.element.appendChild(title);

        // Subtitle
        const subtitle = document.createElement('div');
        subtitle.textContent = 'Web Edition';
        subtitle.style.cssText = 'font-size: 12px; color: #888; margin-bottom: 48px;';
        this.element.appendChild(subtitle);

        // Menu
        const menu = document.createElement('div');
        menu.style.cssText = 'display: flex; flex-direction: column; gap: 16px;';

        const newGameBtn = this.createMenuItem('> NEW GAME', 'menu-new-game');
        newGameBtn.addEventListener('click', () => callbacks.onPlay());
        menu.appendChild(newGameBtn);

        const spectateBtn = this.createMenuItem('> SPECTATE', 'menu-spectate');
        spectateBtn.addEventListener('click', () => callbacks.onSpectate());
        menu.appendChild(spectateBtn);

        this.element.appendChild(menu);

        // Session list (hidden by default)
        this.sessionListEl = document.createElement('div');
        this.sessionListEl.className = 'session-list pixel-border';
        this.sessionListEl.style.cssText = `
            display: none;
            margin-top: 24px;
            padding: 16px;
            background: rgba(0, 0, 0, 0.8);
            max-height: 200px;
            overflow-y: auto;
            min-width: 300px;
        `;
        this.element.appendChild(this.sessionListEl);

        // Footer
        const footer = document.createElement('div');
        footer.textContent = 'WASD to move, Arrow keys to shoot';
        footer.style.cssText = `
            position: absolute;
            bottom: 32px;
            font-size: 10px;
            color: #666;
        `;
        this.element.appendChild(footer);

        this.container.appendChild(this.element);
    }

    private createMenuItem(text: string, className: string): HTMLElement {
        const item = document.createElement('div');
        item.textContent = text;
        item.className = className;
        item.style.cssText = `
            font-size: 16px;
            color: #fff;
            cursor: pointer;
            padding: 8px 16px;
        `;
        item.addEventListener('mouseenter', () => {
            item.style.color = '#ffcc00';
        });
        item.addEventListener('mouseleave', () => {
            item.style.color = '#fff';
        });
        return item;
    }

    showSessionList(sessions: SessionListItem[]): void {
        this.sessionListEl.style.display = 'block';
        this.sessionListEl.innerHTML = '';

        if (sessions.length === 0) {
            this.sessionListEl.innerHTML = '<div style="color: #888;">No active games</div>';
            return;
        }

        for (const session of sessions) {
            const item = document.createElement('div');
            item.style.cssText = `
                padding: 8px;
                cursor: pointer;
                border-bottom: 1px solid #333;
            `;
            const hearts = '♥'.repeat(session.playerHealth);
            item.innerHTML = `
                <span style="color: #fff;">${session.sessionId.slice(0, 8)}</span>
                <span style="color: #888;"> - F${session.floor} - </span>
                <span style="color: #ff0000;">${hearts}</span>
                <span style="color: #888;"> (${session.spectatorCount} watching)</span>
            `;
            item.addEventListener('click', () => {
                this.callbacks.onJoinSession?.(session.sessionId);
            });
            item.addEventListener('mouseenter', () => {
                item.style.background = '#222';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });
            this.sessionListEl.appendChild(item);
        }
    }

    hideSessionList(): void {
        this.sessionListEl.style.display = 'none';
    }

    show(): void {
        this.element.style.display = 'flex';
    }

    hide(): void {
        this.element.style.display = 'none';
    }

    destroy(): void {
        this.element.remove();
    }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`

**Step 5: Commit**

```bash
git add web/src/ui/LandingPage.ts web/src/__tests__/LandingPage.test.ts
git commit -m "feat(web): implement retro landing page component"
```

---

## Task 4: Create SpectatorOverlay component

**Files:**
- Create: `web/src/ui/SpectatorOverlay.ts`
- Create: `web/src/__tests__/SpectatorOverlay.test.ts`

**Step 1: Write the failing test**

```typescript
// web/src/__tests__/SpectatorOverlay.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SpectatorOverlay } from '../ui/SpectatorOverlay';

describe('SpectatorOverlay', () => {
    let container: HTMLElement;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        container.remove();
    });

    it('creates spectator overlay', () => {
        const overlay = new SpectatorOverlay(container);
        expect(container.querySelector('.spectator-overlay')).not.toBeNull();
    });

    it('shows SPECTATOR MODE badge', () => {
        const overlay = new SpectatorOverlay(container);
        expect(container.textContent).toContain('SPECTATOR MODE');
    });

    it('shows watching session ID', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'test123', spectatorCount: 5, playerHealth: 3, floor: 2, items: [], timePlayed: 120 });
        expect(container.textContent).toContain('test123');
    });

    it('shows spectator count', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 5, playerHealth: 3, floor: 2, items: [], timePlayed: 0 });
        expect(container.textContent).toContain('5');
    });

    it('shows player health', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 4, floor: 1, items: [], timePlayed: 0 });
        expect(container.innerHTML).toContain('♥♥♥♥');
    });

    it('shows floor number', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 3, floor: 3, items: [], timePlayed: 0 });
        expect(container.textContent).toContain('Floor 3');
    });

    it('shows time played', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.update({ sessionId: 'abc', spectatorCount: 1, playerHealth: 3, floor: 1, items: [], timePlayed: 125 });
        expect(container.textContent).toContain('2:05');
    });

    it('destroy removes overlay', () => {
        const overlay = new SpectatorOverlay(container);
        overlay.destroy();
        expect(container.querySelector('.spectator-overlay')).toBeNull();
    });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`

**Step 3: Write implementation**

```typescript
// web/src/ui/SpectatorOverlay.ts

export interface SpectatorData {
    sessionId: string;
    spectatorCount: number;
    playerHealth: number;
    floor: number;
    items: string[];
    timePlayed: number; // seconds
}

export class SpectatorOverlay {
    private container: HTMLElement;
    private element: HTMLElement;
    private badge: HTMLElement;
    private watchingEl: HTMLElement;
    private sidebar: HTMLElement;
    private healthEl: HTMLElement;
    private floorEl: HTMLElement;
    private itemsEl: HTMLElement;
    private timeEl: HTMLElement;
    private countEl: HTMLElement;
    private chatEl: HTMLElement;

    constructor(container: HTMLElement) {
        this.container = container;

        this.element = document.createElement('div');
        this.element.className = 'spectator-overlay';

        // Badge (top-left)
        this.badge = document.createElement('div');
        this.badge.className = 'spectator-badge pixel-text';
        this.badge.textContent = 'SPECTATOR MODE';
        this.badge.style.cssText = `
            position: fixed;
            top: 16px;
            left: 16px;
            background: #ff0000;
            color: #fff;
            padding: 8px 12px;
            font-size: 10px;
            z-index: 150;
        `;
        this.element.appendChild(this.badge);

        // Watching label
        this.watchingEl = document.createElement('div');
        this.watchingEl.className = 'spectator-watching pixel-text';
        this.watchingEl.style.cssText = `
            position: fixed;
            top: 48px;
            left: 16px;
            color: #888;
            font-size: 8px;
            z-index: 150;
        `;
        this.element.appendChild(this.watchingEl);

        // Sidebar (right)
        this.sidebar = document.createElement('div');
        this.sidebar.className = 'spectator-sidebar pixel-text pixel-border';
        this.sidebar.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            bottom: 64px;
            width: 180px;
            background: rgba(0, 0, 0, 0.85);
            padding: 12px;
            font-size: 10px;
            z-index: 150;
            display: flex;
            flex-direction: column;
            gap: 12px;
        `;

        // Player info section
        const infoSection = document.createElement('div');
        infoSection.innerHTML = '<div style="color: #888; margin-bottom: 8px;">PLAYER INFO</div>';

        this.healthEl = document.createElement('div');
        this.healthEl.style.color = '#ff0000';
        infoSection.appendChild(this.healthEl);

        this.floorEl = document.createElement('div');
        this.floorEl.style.color = '#fff';
        infoSection.appendChild(this.floorEl);

        this.timeEl = document.createElement('div');
        this.timeEl.style.color = '#888';
        infoSection.appendChild(this.timeEl);

        this.itemsEl = document.createElement('div');
        this.itemsEl.style.cssText = 'color: #ffcc00; margin-top: 8px;';
        infoSection.appendChild(this.itemsEl);

        this.sidebar.appendChild(infoSection);

        // Spectator count
        this.countEl = document.createElement('div');
        this.countEl.style.color = '#888';
        this.sidebar.appendChild(this.countEl);

        // Chat placeholder
        this.chatEl = document.createElement('div');
        this.chatEl.className = 'pixel-border';
        this.chatEl.style.cssText = `
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            padding: 8px;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        `;
        this.chatEl.textContent = 'Chat coming soon...';
        this.sidebar.appendChild(this.chatEl);

        this.element.appendChild(this.sidebar);
        this.container.appendChild(this.element);
    }

    update(data: SpectatorData): void {
        this.watchingEl.textContent = `Watching: ${data.sessionId}`;
        this.healthEl.innerHTML = '♥'.repeat(data.playerHealth);
        this.floorEl.textContent = `Floor ${data.floor}`;
        this.timeEl.textContent = this.formatTime(data.timePlayed);
        this.countEl.textContent = `👁 ${data.spectatorCount} watching`;

        if (data.items.length > 0) {
            this.itemsEl.textContent = `Items: ${data.items.slice(0, 3).join(', ')}`;
        } else {
            this.itemsEl.textContent = '';
        }
    }

    private formatTime(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    show(): void {
        this.element.style.display = 'block';
    }

    hide(): void {
        this.element.style.display = 'none';
    }

    destroy(): void {
        this.element.remove();
    }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`

**Step 5: Commit**

```bash
git add web/src/ui/SpectatorOverlay.ts web/src/__tests__/SpectatorOverlay.test.ts
git commit -m "feat(web): implement spectator overlay component"
```

---

## Task 5: Add session list endpoint to server

**Files:**
- Modify: `src/web/server.py`
- Modify: `src/web/session_manager.py`
- Modify: `src/web/protocol.py`

**Step 1: Add ListSessionsMessage to protocol.py**

Add to `src/web/protocol.py`:
```python
@dataclass
class ListSessionsMessage:
    """Request to list active sessions."""
    pass

@dataclass
class SessionListMessage:
    """Response with list of active sessions."""
    sessions: list  # List of session info dicts
```

Update `parse_message` to handle `list_sessions` type.

**Step 2: Add get_session_list to SessionManager**

Add to `src/web/session_manager.py`:
```python
def get_session_list(self) -> list:
    """Get list of active sessions with basic info."""
    result = []
    for session_id, session in self.sessions.items():
        if session.running:
            info = session.get_session_info()
            result.append(info)
    return result
```

Add to `GameSession`:
```python
def get_session_info(self) -> dict:
    """Get session info for listing."""
    state = self.get_game_state()
    player_health = 3  # default
    floor = 1
    if state and state.get('player'):
        health = state['player'].get('components', {}).get('health', {})
        player_health = health.get('current', 3)
    return {
        'sessionId': self.session_id,
        'playerHealth': player_health,
        'floor': floor,
        'spectatorCount': len(self.spectators)
    }
```

**Step 3: Handle list_sessions in server.py**

In `handle_client`, add handling for list_sessions message:
```python
elif isinstance(msg, ListSessionsMessage):
    sessions = self.session_manager.get_session_list()
    response = SessionListMessage(sessions=sessions)
    await websocket.send(serialize_message(response))
```

**Step 4: Add tests**

Create `tests/test_session_list.py` with tests for the new functionality.

**Step 5: Run tests and commit**

```bash
uv run pytest tests/test_session_list.py -v
git add src/web/ tests/test_session_list.py
git commit -m "feat(server): add session listing endpoint"
```

---

## Task 6: Update NetworkClient for session listing

**Files:**
- Modify: `web/src/network.ts`

**Step 1: Add session listing methods**

Add to NetworkClient class:
```typescript
/**
 * Request list of active sessions.
 */
requestSessionList(): void {
    this.send({ type: 'list_sessions' });
}
```

Add handler in `handleMessage`:
```typescript
else if (data.type === 'session_list') {
    this.handlers.onSessionList?.(data.sessions);
}
```

Add to NetworkEventHandler:
```typescript
onSessionList?: (sessions: SessionListItem[]) => void;
```

**Step 2: Commit**

```bash
git add web/src/network.ts
git commit -m "feat(web): add session list support to NetworkClient"
```

---

## Task 7: Update UIManager to orchestrate components

**Files:**
- Modify: `web/src/ui.ts`

**Step 1: Refactor UIManager**

Replace existing UIManager with new version that uses HUD, LandingPage, and SpectatorOverlay:

```typescript
// web/src/ui.ts
import { HUD, HUDData } from './ui/HUD';
import { LandingPage, SessionListItem } from './ui/LandingPage';
import { SpectatorOverlay, SpectatorData } from './ui/SpectatorOverlay';

export interface UICallbacks {
    onPlay: () => void;
    onSpectate: () => void;
    onJoinSession: (sessionId: string) => void;
}

export class UIManager {
    private hud: HUD;
    private landingPage: LandingPage;
    private spectatorOverlay: SpectatorOverlay | null = null;
    private container: HTMLElement;
    private isSpectator: boolean = false;

    constructor(container: HTMLElement, callbacks: UICallbacks) {
        this.container = container;

        // Create components
        this.hud = new HUD(container);
        this.hud.hide();

        this.landingPage = new LandingPage(container, {
            onPlay: callbacks.onPlay,
            onSpectate: callbacks.onSpectate,
            onJoinSession: callbacks.onJoinSession
        });
    }

    showLandingPage(): void {
        this.landingPage.show();
        this.hud.hide();
        this.spectatorOverlay?.hide();
    }

    showGame(isSpectator: boolean = false): void {
        this.isSpectator = isSpectator;
        this.landingPage.hide();
        this.hud.show();

        if (isSpectator) {
            if (!this.spectatorOverlay) {
                this.spectatorOverlay = new SpectatorOverlay(this.container);
            }
            this.spectatorOverlay.show();
        } else {
            this.spectatorOverlay?.hide();
        }
    }

    updateHUD(data: HUDData): void {
        this.hud.update(data);
    }

    updateSpectatorOverlay(data: SpectatorData): void {
        this.spectatorOverlay?.update(data);
    }

    showSessionList(sessions: SessionListItem[]): void {
        this.landingPage.showSessionList(sessions);
    }

    destroy(): void {
        this.hud.destroy();
        this.landingPage.destroy();
        this.spectatorOverlay?.destroy();
    }
}

// Re-export types for convenience
export { HUDData } from './ui/HUD';
export { SessionListItem } from './ui/LandingPage';
export { SpectatorData } from './ui/SpectatorOverlay';
```

**Step 2: Commit**

```bash
git add web/src/ui.ts
git commit -m "refactor(web): update UIManager to use new components"
```

---

## Task 8: Update main.ts for new UI flow

**Files:**
- Modify: `web/src/main.ts`

**Step 1: Refactor main.ts to use new UI flow**

Update main.ts:
- Initialize UIManager with callbacks
- Show landing page initially
- Handle play/spectate/join actions
- Wire up session list fetching
- Update HUD and spectator overlay on game state

**Step 2: Test manually**

Run: `npm run dev` and verify:
- Landing page shows on load
- NEW GAME starts a player session
- SPECTATE requests session list
- Session selection joins as spectator
- HUD shows during gameplay
- Spectator overlay shows for spectators

**Step 3: Commit**

```bash
git add web/src/main.ts
git commit -m "feat(web): integrate new UI flow in main"
```

---

## Task 9: Final verification

**Step 1: Run all tests**

```bash
cd web && npm test
cd .. && uv run pytest
```

**Step 2: Verify TypeScript**

```bash
npx tsc --noEmit
```

**Step 3: Manual testing**

Test full flow:
- Landing page display
- NEW GAME flow
- SPECTATE flow
- Session list
- HUD updates
- Spectator overlay

**Step 4: Final commit if needed**

```bash
git add -A
git commit -m "chore(web): final verification and cleanup"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Add pixel font and base styles | index.html, styles.css, main.ts |
| 2 | Create HUD component | HUD.ts, HUD.test.ts |
| 3 | Create LandingPage component | LandingPage.ts, LandingPage.test.ts |
| 4 | Create SpectatorOverlay component | SpectatorOverlay.ts, SpectatorOverlay.test.ts |
| 5 | Add session list endpoint | server.py, session_manager.py, protocol.py |
| 6 | Update NetworkClient | network.ts |
| 7 | Update UIManager | ui.ts |
| 8 | Update main.ts | main.ts |
| 9 | Final verification | all |
