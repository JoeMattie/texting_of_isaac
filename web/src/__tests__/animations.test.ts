import { describe, it, expect } from 'vitest';
import { ANIMATION_CONFIGS, EntityType, calculateBobOffset } from '../animations';

describe('Animation Configs', () => {
  it('should have config for player', () => {
    expect(ANIMATION_CONFIGS.player).toBeDefined();
    expect(ANIMATION_CONFIGS.player.bob).toBeDefined();
  });

  it('should have config for all enemy types', () => {
    const enemyTypes: EntityType[] = [
      'enemy_chaser', 'enemy_shooter', 'enemy_orbiter', 'enemy_turret', 'enemy_tank'
    ];
    for (const type of enemyTypes) {
      expect(ANIMATION_CONFIGS[type]).toBeDefined();
    }
  });

  it('should have config for pickups', () => {
    const pickupTypes: EntityType[] = ['heart', 'coin', 'bomb', 'item'];
    for (const type of pickupTypes) {
      expect(ANIMATION_CONFIGS[type]).toBeDefined();
      expect(ANIMATION_CONFIGS[type].bob).toBeDefined();
    }
  });
});

describe('calculateBobOffset', () => {
  it('should return 0 at time 0', () => {
    const offset = calculateBobOffset(0, { amplitude: 2, frequency: 2 });
    expect(offset).toBeCloseTo(0, 5);
  });

  it('should return amplitude at quarter period', () => {
    // At t = 1/(4*frequency), sin(2*pi*f*t) = sin(pi/2) = 1
    const frequency = 2;
    const amplitude = 2;
    const quarterPeriod = 1 / (4 * frequency);
    const offset = calculateBobOffset(quarterPeriod, { amplitude, frequency });
    expect(offset).toBeCloseTo(amplitude, 5);
  });

  it('should return negative amplitude at 3/4 period', () => {
    const frequency = 2;
    const amplitude = 2;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const offset = calculateBobOffset(threeQuarterPeriod, { amplitude, frequency });
    expect(offset).toBeCloseTo(-amplitude, 5);
  });

  it('should return 0 at full period', () => {
    const frequency = 2;
    const fullPeriod = 1 / frequency;
    const offset = calculateBobOffset(fullPeriod, { amplitude: 5, frequency });
    expect(offset).toBeCloseTo(0, 5);
  });
});
