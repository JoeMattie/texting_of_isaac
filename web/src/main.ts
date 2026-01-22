import * as PIXI from 'pixi.js';

async function main() {
    console.log('Texting of Isaac - Web Edition');
    console.log('Pixi.js version:', PIXI.VERSION);

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

    // Test rendering
    const text = new PIXI.Text({
        text: 'Texting of Isaac',
        style: {
            fontFamily: 'monospace',
            fontSize: 48,
            fill: 0x00ff00
        }
    });
    text.anchor.set(0.5);
    text.position.set(app.screen.width / 2, app.screen.height / 2);
    app.stage.addChild(text);
}

main();
