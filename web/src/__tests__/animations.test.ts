import { describe, it, expect } from 'vitest';
import {
  ANIMATION_CONFIGS,
  EntityType,
  calculateBobOffset,
  calculatePulseScale,
  calculateRotation,
  calculateWobble
} from '../animations';

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

describe('calculatePulseScale', () => {
  it('should return midpoint scale at time 0', () => {
    const scale = calculatePulseScale(0, { minScale: 1.0, maxScale: 1.2, frequency: 2 });
    // sin(0) = 0, so scale = midpoint = 1.1
    expect(scale).toBeCloseTo(1.1, 5);
  });

  it('should return maxScale at quarter period', () => {
    const frequency = 2;
    const quarterPeriod = 1 / (4 * frequency);
    const scale = calculatePulseScale(quarterPeriod, { minScale: 1.0, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.2, 5);
  });

  it('should return minScale at 3/4 period', () => {
    const frequency = 2;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const scale = calculatePulseScale(threeQuarterPeriod, { minScale: 1.0, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.0, 5);
  });

  it('should handle asymmetric min/max', () => {
    const frequency = 1;
    const quarterPeriod = 0.25;
    const scale = calculatePulseScale(quarterPeriod, { minScale: 0.8, maxScale: 1.2, frequency });
    expect(scale).toBeCloseTo(1.2, 5);
  });
});

describe('calculateRotation', () => {
  it('should return 0 at time 0', () => {
    const rotation = calculateRotation(0, { speed: 360 });
    expect(rotation).toBeCloseTo(0, 5);
  });

  it('should return speed after 1 second', () => {
    const rotation = calculateRotation(1, { speed: 360 });
    expect(rotation).toBeCloseTo(360, 5);
  });

  it('should accumulate over time', () => {
    const rotation = calculateRotation(2.5, { speed: 90 });
    expect(rotation).toBeCloseTo(225, 5);
  });
});

describe('calculateWobble', () => {
  it('should return 0 at time 0', () => {
    const angle = calculateWobble(0, { angle: 15, frequency: 8 });
    expect(angle).toBeCloseTo(0, 5);
  });

  it('should return max angle at quarter period', () => {
    const frequency = 8;
    const quarterPeriod = 1 / (4 * frequency);
    const angle = calculateWobble(quarterPeriod, { angle: 15, frequency });
    expect(angle).toBeCloseTo(15, 5);
  });

  it('should return negative max angle at 3/4 period', () => {
    const frequency = 8;
    const threeQuarterPeriod = 3 / (4 * frequency);
    const angle = calculateWobble(threeQuarterPeriod, { angle: 15, frequency });
    expect(angle).toBeCloseTo(-15, 5);
  });
});
