import { describe, it, expect } from 'vitest';
import { ANIMATION_CONFIGS, EntityType } from '../animations';

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
