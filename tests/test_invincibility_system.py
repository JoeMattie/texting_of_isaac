"""Tests for invincibility system."""
import esper
import pytest
from src.systems.invincibility import InvincibilitySystem
from src.components.game import Invincible


def test_invincibility_system_decrements_timer():
    """Test InvincibilitySystem reduces remaining time."""
    esper.switch_world("test_invincibility")
    esper.clear_database()

    # Create entity with invincibility
    entity = esper.create_entity()
    esper.add_component(entity, Invincible(0.5))

    # Process system
    system = InvincibilitySystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Check timer decreased
    invincible = esper.component_for_entity(entity, Invincible)
    assert invincible.remaining == pytest.approx(0.4)


def test_invincibility_removed_when_expired():
    """Test Invincible component removed at 0."""
    esper.switch_world("test_invincibility_removal")
    esper.clear_database()

    entity = esper.create_entity()
    esper.add_component(entity, Invincible(0.05))

    system = InvincibilitySystem()
    system.dt = 0.1
    esper.add_processor(system)
    esper.process()

    # Component should be removed
    assert not esper.has_component(entity, Invincible)


def test_invincibility_system_handles_multiple_entities():
    """Test system handles multiple invincible entities."""
    esper.switch_world("test_invincibility_multiple")
    esper.clear_database()

    entity1 = esper.create_entity()
    esper.add_component(entity1, Invincible(0.5))

    entity2 = esper.create_entity()
    esper.add_component(entity2, Invincible(0.1))

    system = InvincibilitySystem()
    system.dt = 0.15
    esper.add_processor(system)
    esper.process()

    # Entity1 still invincible
    assert esper.has_component(entity1, Invincible)
    inv1 = esper.component_for_entity(entity1, Invincible)
    assert inv1.remaining == pytest.approx(0.35)

    # Entity2 no longer invincible
    assert not esper.has_component(entity2, Invincible)
