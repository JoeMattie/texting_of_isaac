# Deployment Guide

## Overview

The Texting of Isaac web frontend consists of two services:
- **Python WebSocket Server** (backend)
- **Static Frontend** (built with Vite)

## Prerequisites

- Backend hosting with WebSocket support (Railway, Render, DigitalOcean)
- Static hosting for frontend (Netlify, Vercel, Cloudflare Pages)
- Custom domain (optional)

## Backend Deployment

### Option 1: Railway

1. Create new project on Railway
2. Add GitHub repository
3. Configure build settings:
   - Build Command: `uv sync`
   - Start Command: `uv run python -m src.web.server`
   - Port: 8765
4. Add environment variables (if needed)
5. Deploy

### Option 2: Render

1. Create new Web Service
2. Connect GitHub repository
3. Configure:
   - Build Command: `uv sync`
   - Start Command: `uv run python -m src.web.server`
   - Port: 8765
4. Deploy

### Option 3: DigitalOcean App Platform

1. Create new App
2. Connect GitHub repository
3. Configure:
   - Build Command: `uv sync`
   - Run Command: `uv run python -m src.web.server`
   - Port: 8765
4. Deploy

## Frontend Deployment

### Option 1: Netlify

1. Create new site from Git
2. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `web/dist`
   - Base directory: `web`
3. Add environment variable:
   - `VITE_WS_URL` = `wss://your-backend-url.com`
4. Deploy

### Option 2: Vercel

1. Import project
2. Configure:
   - Framework Preset: Vite
   - Root Directory: `web`
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Add environment variable:
   - `VITE_WS_URL` = `wss://your-backend-url.com`
4. Deploy

### Option 3: Cloudflare Pages

1. Connect GitHub repository
2. Configure build:
   - Framework preset: Vite
   - Build command: `npm run build`
   - Build output directory: `web/dist`
   - Root directory: `web`
3. Add environment variable:
   - `VITE_WS_URL` = `wss://your-backend-url.com`
4. Deploy

## Environment Variables

### Backend

No environment variables required for basic setup. Optional:
- `HOST` - Server host (default: localhost)
- `PORT` - Server port (default: 8765)

### Frontend

Required:
- `VITE_WS_URL` - WebSocket server URL (must use `wss://` for production)

## Testing Production Build

### Test Backend Locally

```bash
uv run python -m src.web.server
```

### Test Frontend Locally

```bash
cd web
npm run build
npm run preview
```

Open `http://localhost:4173` and verify connection works.

## Security Checklist

- [ ] Frontend uses `wss://` (not `ws://`) for WebSocket connections
- [ ] Backend server has CORS configured (if needed)
- [ ] Environment variables not committed to Git
- [ ] Production builds are minified and optimized
- [ ] WebSocket server only accepts valid game state messages

## Monitoring

### Backend Metrics
- WebSocket connection count
- Active session count
- Message throughput
- CPU/Memory usage

### Frontend Metrics
- Page load time
- FPS (frames per second)
- Network traffic
- WebSocket reconnection rate

## Troubleshooting

### Common Issues

**Frontend can't connect to backend:**
- Verify `VITE_WS_URL` environment variable is set correctly
- Check if backend is using `wss://` (not `ws://`)
- Ensure backend server allows WebSocket connections
- Check CORS headers if needed

**Build fails:**
- Run `npm install` to ensure dependencies are installed
- Clear `web/node_modules` and reinstall
- Check Node.js version (requires 18+)

**Backend not starting:**
- Verify Python 3.12+ is installed
- Run `uv sync` to install dependencies
- Check if port 8765 is available

## Rollback

If deployment fails:
1. Revert Git commit
2. Redeploy previous working version
3. Check logs for errors
4. Monitor WebSocket connections after rollback

## Performance Optimization

### Backend
- Use a reverse proxy (nginx) for production deployments
- Enable gzip compression for WebSocket messages
- Monitor memory usage for long-running sessions

### Frontend
- Enable CDN for static assets
- Use HTTP/2 for faster asset loading
- Monitor bundle size (currently ~520 KB total)

## Next Steps

Once deployed:
- Test with multiple concurrent users
- Monitor performance metrics
- Set up error tracking (Sentry, etc.)
- Configure CDN for static assets
- Add health check endpoints
- Set up automated deployment CI/CD

## Development vs Production

### Key Differences

| Feature | Development | Production |
|---------|-------------|-----------|
| WebSocket URL | `ws://localhost:8765` | `wss://your-domain.com` |
| Source Maps | Enabled | Disabled |
| Minification | Disabled | Enabled |
| Hot Reload | Enabled | N/A |
| Build Size | Unoptimized | ~520 KB gzipped |

## Support

For issues or questions:
- Check the [README.md](README.md) for project documentation
- Review [WEB_FRONTEND_GUIDE.md](WEB_FRONTEND_GUIDE.md) for technical details
- Open an issue on GitHub
