# Phase 4 UI Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add polished retro-game UI with HUD, landing page, and spectator mode.

**Architecture:** Modular UI components orchestrated by UIManager. Retro pixel aesthetic throughout.

**Tech Stack:** TypeScript, HTML/CSS, Press Start 2P font

---

## HUD Design (Retro Game Style)

**Layout:** Fixed bar at bottom of screen, full width, pixelated border.

**Elements (left to right):**
- Health: Red pixel hearts (♥) for current, gray for missing
- Coins: Gold coin icon + count
- Bombs: Bomb icon + count
- Items: Small icons in a row (max 6 visible)
- Floor/Room: "B1" or "F2" indicator on right side

**Styling:**
- Black background with 2px white pixelated border
- Chunky pixel font (Press Start 2P from Google Fonts)
- 8-bit color palette: red (#ff0000), gold (#ffcc00), white (#ffffff)
- Fixed height: 48px

---

## Landing Page (Game-Styled Title Screen)

**Layout:** Fullscreen dark background, centered content.

**Elements:**
- Title: "TEXTING OF ISAAC" in large pixel font, subtle glow effect
- Subtitle: "Web Edition" smaller underneath
- Menu options (styled like classic game menu):
  - `> NEW GAME` - Starts as player
  - `> SPECTATE` - Shows session list
- Session list (when Spectate selected):
  - Scrollable list with pixelated border
  - Each entry: "Player [ID] - Floor [X] - [health hearts]"
  - Click to join as spectator
- Footer: "WASD to move, Arrow keys to shoot"

**Styling:**
- Scanline overlay effect (subtle CSS)
- Menu items highlight on hover (color change)
- Press Start 2P font throughout

---

## Spectator Mode (Stream-Style)

**Layout:** Game view centered, sidebar on right.

**Top overlay:**
- "SPECTATOR MODE" badge (pixelated, red background)
- "Watching: [session ID]" below badge

**Right sidebar (200px wide):**
- Player info panel:
  - Current health
  - Floor number
  - Items collected
  - Time played
- Spectator count: "👁 N watching"
- Chat/reactions area (placeholder for future):
  - Empty box with "Chat coming soon..." text
  - Or simple reaction buttons that show intent

**Styling:**
- Sidebar has same retro border as HUD
- Semi-transparent dark background
- Matches overall pixel aesthetic

---

## File Structure

```
web/src/
├── ui/
│   ├── HUD.ts              # Bottom HUD bar component
│   ├── LandingPage.ts      # Title screen with menu
│   ├── SpectatorOverlay.ts # Badge + sidebar
│   └── styles.css          # Shared retro styles, pixel font
├── ui.ts                   # Updated UIManager
└── index.html              # Add font link
```

---

## Application Flow

1. App starts → Show LandingPage
2. User clicks "NEW GAME" → Connect as player, hide LandingPage, show HUD
3. User clicks "SPECTATE" → Fetch session list, show list
4. User selects session → Connect as spectator, show HUD + SpectatorOverlay

---

## Server Changes

Need to add session listing capability:

**New message type:** `list_sessions`
- Client sends: `{"type": "list_sessions"}`
- Server responds: `{"type": "session_list", "sessions": [...]}`

**Session info in list:**
```json
{
  "sessionId": "abc123",
  "playerHealth": 3,
  "floor": 1,
  "spectatorCount": 2,
  "startedAt": "2026-01-22T12:00:00Z"
}
```

---

## Testing

**Test files:**
- `web/src/__tests__/HUD.test.ts`
- `web/src/__tests__/LandingPage.test.ts`
- `web/src/__tests__/SpectatorOverlay.test.ts`

**Key test cases:**
- HUD renders health hearts correctly
- HUD updates on state change
- LandingPage shows menu options
- LandingPage switches to session list on Spectate click
- SpectatorOverlay shows badge and sidebar
- Session list displays entries correctly
